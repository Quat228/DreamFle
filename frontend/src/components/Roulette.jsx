import React, { useState, useEffect, useRef, useImperativeHandle, forwardRef } from 'react';
import './Roulette.css';

const Roulette = forwardRef(({ entryIds = [], entryQuantities = {} }, ref) => {
  const [rotation, setRotation] = useState(0);
  const [isSpinning, setIsSpinning] = useState(false);
  const [winnerEntryId, setWinnerEntryId] = useState(null);
  const animationFrameRef = useRef(null);
  const stopTimeoutRef = useRef(null);
  const rotationSpeedRef = useRef(0);

  // Calculate pie slices based on quantities
  const calculateSlices = () => {
    if (!entryIds || entryIds.length === 0) return [];

    // Calculate total quantity
    const totalQuantity = entryIds.reduce((sum, id) => {
      return sum + (entryQuantities[id] || 1);
    }, 0);

    if (totalQuantity === 0) return [];

    // Calculate angles for each slice
    const slices = [];
    let currentAngle = -90; // Start from top (-90 degrees)

    entryIds.forEach((entryId, index) => {
      const quantity = entryQuantities[entryId] || 1;
      const percentage = quantity / totalQuantity;
      const angle = percentage * 360;

      slices.push({
        id: entryId,
        quantity: quantity,
        startAngle: currentAngle,
        endAngle: currentAngle + angle,
        percentage: percentage,
        color: getColorForIndex(index),
      });

      currentAngle += angle;
    });

    return slices;
  };

  // Generate color for each slice
  const getColorForIndex = (index) => {
    const colors = [
      '#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe',
      '#00f2fe', '#43e97b', '#fa709a', '#fee140', '#30cfd0',
      '#a8edea', '#fed6e3', '#ff9a9e', '#fecfef', '#ffecd2',
    ];
    return colors[index % colors.length];
  };

  // Convert angle to path for SVG pie slice
  const createSlicePath = (centerX, centerY, radius, startAngle, endAngle) => {
    const startRad = (startAngle * Math.PI) / 180;
    const endRad = (endAngle * Math.PI) / 180;

    const x1 = centerX + radius * Math.cos(startRad);
    const y1 = centerY + radius * Math.sin(startRad);
    const x2 = centerX + radius * Math.cos(endRad);
    const y2 = centerY + radius * Math.sin(endRad);

    const largeArcFlag = endAngle - startAngle > 180 ? 1 : 0;

    return `M ${centerX} ${centerY} L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2} Z`;
  };

  // Calculate which slice is at the top (winning position)
  const getSliceAtTop = (slices, currentRotation) => {
    // Top position is at -90 degrees (accounting for rotation)
    const topAngle = (-90 - currentRotation + 360) % 360;
    
    for (const slice of slices) {
      let startAngle = (slice.startAngle + 360) % 360;
      let endAngle = (slice.endAngle + 360) % 360;
      
      // Handle wrap-around
      if (endAngle < startAngle) {
        endAngle += 360;
      }
      
      let checkAngle = topAngle;
      if (checkAngle < startAngle) {
        checkAngle += 360;
      }
      
      if (checkAngle >= startAngle && checkAngle < endAngle) {
        return slice;
      }
    }
    
    return slices[0]; // Fallback
  };

  // Expose methods to parent component via ref
  useImperativeHandle(ref, () => ({
    start: () => {
      setIsSpinning(true);
      setWinnerEntryId(null);
      rotationSpeedRef.current = 15; // Initial spin speed (degrees per frame)
      setRotation(0);
    },
    stopOnEntry: (entryId) => {
      if (stopTimeoutRef.current) {
        clearTimeout(stopTimeoutRef.current);
      }
      
      const slices = calculateSlices();
      const winnerSlice = slices.find(s => s.id === entryId);
      
      if (!winnerSlice) {
        setIsSpinning(false);
        rotationSpeedRef.current = 0;
        return;
      }
      
      // Calculate the center angle of the winner slice
      const winnerCenterAngle = (winnerSlice.startAngle + winnerSlice.endAngle) / 2;
      
      // To center winner at top (-90 degrees), we need: winnerCenterAngle + rotation = -90
      // So: rotation = -90 - winnerCenterAngle
      // But we want to add several full rotations for visual effect
      const baseRotation = -winnerCenterAngle - 90;
      
      // Get current rotation (normalized)
      const currentRotation = rotation;
      
      // Add 3-5 full rotations plus the base rotation
      const extraRotations = 3 * 360 + (Math.random() * 2 * 360); // 3-5 full spins
      const finalRotation = currentRotation + extraRotations + baseRotation;
      
      // Start slowing down
      const startSlowdown = () => {
        const slowDown = () => {
          if (rotationSpeedRef.current > 0.3) {
            rotationSpeedRef.current *= 0.97; // Gradual slowdown
            requestAnimationFrame(slowDown);
          } else {
            // Stop animation and set final position
            if (animationFrameRef.current) {
              cancelAnimationFrame(animationFrameRef.current);
              animationFrameRef.current = null;
            }
            setIsSpinning(false);
            rotationSpeedRef.current = 0;
            
            // Set final rotation to center winner
            setRotation(finalRotation);
            setWinnerEntryId(entryId);
          }
        };
        slowDown();
      };
      
      // Start slowing down after a delay
      stopTimeoutRef.current = setTimeout(() => {
        startSlowdown();
      }, 500);
    },
    reset: () => {
      setRotation(0);
      setIsSpinning(false);
      setWinnerEntryId(null);
      rotationSpeedRef.current = 0;
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
      if (stopTimeoutRef.current) {
        clearTimeout(stopTimeoutRef.current);
        stopTimeoutRef.current = null;
      }
    }
  }));

  // Spinning animation
  useEffect(() => {
    if (isSpinning && rotationSpeedRef.current > 0) {
      const animate = () => {
        setRotation(prev => (prev + rotationSpeedRef.current) % 360);
        animationFrameRef.current = requestAnimationFrame(animate);
      };
      
      animationFrameRef.current = requestAnimationFrame(animate);
    }

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
    };
  }, [isSpinning]);

  const slices = calculateSlices();
  const radius = 120;
  const centerX = 140;
  const centerY = 140;
  const viewBoxSize = 280;

  if (slices.length === 0) {
    return (
      <div className="roulette-container">
        <div className="roulette-empty">No entries available</div>
      </div>
    );
  }

  return (
    <div className="roulette-container">
      <div className="roulette-wheel-wrapper">
        <svg
          width="280"
          height="280"
          viewBox={`0 0 ${viewBoxSize} ${viewBoxSize}`}
          className="roulette-svg"
          style={{
            transform: `rotate(${rotation}deg)`,
            transition: isSpinning ? 'none' : 'transform 0.5s ease-out',
          }}
        >
          {slices.map((slice, index) => {
            const path = createSlicePath(centerX, centerY, radius, slice.startAngle, slice.endAngle);
            const isWinner = winnerEntryId === slice.id;
            const sliceCenterAngle = (slice.startAngle + slice.endAngle) / 2;
            const textX = centerX + (radius * 0.7) * Math.cos((sliceCenterAngle * Math.PI) / 180);
            const textY = centerY + (radius * 0.7) * Math.sin((sliceCenterAngle * Math.PI) / 180);

            return (
              <g key={slice.id}>
                <path
                  d={path}
                  fill={slice.color}
                  stroke="#fff"
                  strokeWidth="2"
                  className={isWinner ? 'winner-slice' : ''}
                />
                {slice.percentage > 0.05 && ( // Only show text if slice is large enough
                  <text
                    x={textX}
                    y={textY}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fill="white"
                    fontSize="12"
                    fontWeight="bold"
                    className="slice-label"
                    style={{
                      transform: `rotate(${sliceCenterAngle + 90}deg)`,
                      transformOrigin: `${textX}px ${textY}px`,
                    }}
                  >
                    #{slice.id}
                  </text>
                )}
              </g>
            );
          })}
        </svg>
        {/* Pointer indicator at top */}
        <div className="roulette-pointer"></div>
      </div>
      {winnerEntryId && (
        <div className="winner-announcement-badge">
          <div className="winner-icon">🎉</div>
          <div className="winner-text">Winner: Entry #{winnerEntryId}</div>
        </div>
      )}
      {isSpinning && (
        <div className="spinning-indicator">Spinning...</div>
      )}
    </div>
  );
});

Roulette.displayName = 'Roulette';

export default Roulette;
