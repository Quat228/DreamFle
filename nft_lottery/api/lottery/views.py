from datetime import timedelta
from django.db.models import Q
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone

from lottery.models import Raffle, Entry

from .serializers import RaffleSerializer, EntrySerializer


class RaffleListAPIView(ListAPIView):
    """
    GET /api/lottery/raffles/
    Returns list of active raffles.
    """
    serializer_class = RaffleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return active raffles that are not finished
        return Raffle.objects.filter(
            is_active=True, 
            is_finished=False
        ).select_related('prize', 'type').prefetch_related('entries')


class PreviousRafflesAPIView(ListAPIView):
    """
    GET /api/lottery/raffles/previous/
    Returns list of inactive/finished raffles with winners.
    """
    serializer_class = RaffleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return inactive or finished raffles
        return Raffle.objects.filter(
            Q(is_active=False) | Q(is_finished=True)
        ).select_related('prize', 'type', 'winner', 'winner__user', 'winner__entry').prefetch_related('entries').order_by('-created_at')


class RaffleDetailAPIView(RetrieveAPIView):
    """
    GET /api/lottery/raffles/<id>/
    Returns one raffle with full details.
    """
    queryset = Raffle.objects.select_related('prize', 'type').prefetch_related('entries')
    serializer_class = RaffleSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"


class MyEntriesAPIView(ListAPIView):
    """
    GET /api/lottery/entries/
    Returns list of entries for the current user.
    """
    serializer_class = EntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (Entry.objects.filter(user=self.request.user)
                .select_related('raffle', 'raffle__prize', 'raffle__type', 'raffle__winner', 'raffle__winner__user'))


class RaffleTransparencyAPIView(APIView):
    """
    GET /api/lottery/raffles/<id>/transparency/
    Returns transparency data for winner selection verification.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            raffle = Raffle.objects.select_related('prize', 'type', 'winner').get(id=id)
        except Raffle.DoesNotExist:
            return Response(
                {"detail": "Raffle not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not raffle.is_finished:
            return Response({
                "raffle_id": raffle.id,
                "raffle_name": raffle.name,
                "is_finished": False,
                "message": "Raffle has not finished yet. Transparency data will be available after winner selection.",
            })
        
        # Get all entries with their quantities (including bonus entries)
        entries = list(raffle.entries.all().order_by('id'))
        entry_ids = [str(entry.id) for entry in entries]
        entry_quantities = {str(entry.id): entry.quantity + entry.quantity_bonus for entry in entries}
        total_entries = sum(entry.quantity + entry.quantity_bonus for entry in entries)
        
        # Build transparency data
        transparency_data = {
            "raffle_id": raffle.id,
            "raffle_name": raffle.name,
            "is_finished": True,
            "selection_method": "SHA256 hash-based selection with quantity weighting",
            "selection_seed": raffle.winner_selection_seed,
            "selection_hash": raffle.winner_selection_hash,
            "selection_timestamp": raffle.winner_selection_timestamp.isoformat() if raffle.winner_selection_timestamp else None,
            "total_entries": total_entries,
            "total_entry_records": len(entries),
            "entry_ids": entry_ids,
            "entry_quantities": entry_quantities,
            "verification_instructions": {
                "step1": "Combine seed, entry IDs, quantities, and bonus: seed + ','.join(sorted_entry_ids) + ':' + ','.join(entry_id:quantity:quantity_bonus)",
                "step2": "Generate SHA256 hash of the combined string",
                "step3": "Expand entries by quantity + quantity_bonus (each entry appears quantity + quantity_bonus times in selection pool)",
                "step4": "Convert hash to integer: int(hash, 16) % total_entries",
                "step5": "Select entry at that index from expanded entry list",
                "step6": "Verify the selected entry matches the winner",
            },
        }
        
        if hasattr(raffle, 'winner') and raffle.winner:
            transparency_data["winner"] = {
                "user_id": raffle.winner.user.id,
                "username": raffle.winner.user.username,
                "entry_id": raffle.winner.entry.id if raffle.winner.entry else None,
            }
        
        return Response(transparency_data)


class ActiveRaffleStateAPIView(APIView):
    """
    GET /api/lottery/active-raffle/state
    Returns global state for active raffle (used for popup on all pages).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        
        # Find active raffle that is in COUNTDOWN, FINISHING, or FINISHED status
        # Priority: FINISHING > COUNTDOWN > FINISHED
        raffle = None
        
        # Check for FINISHING first
        raffle = Raffle.objects.filter(
            is_active=True,
            status__in=["FINISHING", "FINISHED"],
            start_at__lte=now
        ).order_by('-start_at').first()
        
        # If no FINISHING/FINISHED, check for COUNTDOWN
        if not raffle:
            raffle = Raffle.objects.filter(
                is_active=True,
                status="COUNTDOWN",
                start_at__isnull=False
            ).order_by('-start_at').first()
        
        if not raffle:
            return Response({"active": False})
        
        # Calculate seconds left until start (for COUNTDOWN) or since start (for FINISHING/FINISHED)
        if raffle.start_at:
            if raffle.status == "COUNTDOWN":
                seconds_left = max(0, int((raffle.start_at - now).total_seconds()))
            else:
                # For FINISHING/FINISHED, show 0 or negative
                seconds_left = int((raffle.start_at - now).total_seconds())
        else:
            seconds_left = 0
        
        return Response({
            "active": True,
            "raffle_id": raffle.id,
            "status": raffle.status,
            "seconds_left": seconds_left,
            "live_url": f"/raffle/{raffle.id}/live"
        })


class RaffleLiveAPIView(APIView):
    """
    GET /api/lottery/raffles/<id>/live/
    Returns live raffle status for the winner selection page.
    Status-based response format.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            raffle = (Raffle.objects.select_related('prize', 'type', 'winner', 'winner__user', 'winner__entry')
                      .prefetch_related('entries').get(id=id))
        except Raffle.DoesNotExist:
            return Response(
                {"detail": "Raffle not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get all entries with their quantities
        entries = list(raffle.entries.all().order_by('id'))
        entry_ids = [str(entry.id) for entry in entries]
        entry_quantities = {str(entry.id): entry.quantity + entry.quantity_bonus for entry in entries}
        
        # Prepare entries list for response
        entries_data = [
            {
                "id": str(entry.id),
                "quantity": entry.quantity + entry.quantity_bonus
            }
            for entry in entries
        ]
        
        # Prepare response based on status
        response_data = {
            "status": raffle.status,
            "raffle_id": raffle.id,
            "raffle_name": raffle.name,
            "entries": entries_data,
            "entry_ids": entry_ids,
            "entry_quantities": entry_quantities,
        }
        
        # Add winner information if available
        if raffle.status in ["FINISHING", "FINISHED"] and hasattr(raffle, 'winner') and raffle.winner:
            response_data["winner"] = {
                "entry_id": str(raffle.winner.entry.id) if raffle.winner.entry else None,
                "user": raffle.winner.user.username,
                "user_id": raffle.winner.user.id,
            }
        else:
            response_data["winner"] = None
        
        return Response(response_data)

