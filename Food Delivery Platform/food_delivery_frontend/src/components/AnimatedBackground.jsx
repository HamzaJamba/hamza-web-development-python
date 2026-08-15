import { useMemo } from "react";

/**
 * Full-screen animated background: soft glow shift + rising marigold embers.
 * Pure CSS/SVG — no video file needed, so it stays lightweight and licence-free.
 * Sits behind content (z-index: 0), page content should have position: relative + z-index: 1.
 */
export default function AnimatedBackground({ particleCount = 18 }) {
  const particles = useMemo(
    () =>
      Array.from({ length: particleCount }, (_, i) => ({
        id: i,
        left: Math.random() * 100,
        size: 3 + Math.random() * 6,
        duration: 8 + Math.random() * 10,
        delay: Math.random() * 10,
        drift: (Math.random() - 0.5) * 80,
        opacity: 0.3 + Math.random() * 0.5,
      })),
    [particleCount]
  );

  return (
    <div className="animated-bg" aria-hidden="true">
      {particles.map((p) => (
        <span
          key={p.id}
          className="particle"
          style={{
            left: `${p.left}%`,
            width: p.size,
            height: p.size,
            animationDuration: `${p.duration}s`,
            animationDelay: `${p.delay}s`,
            "--drift": `${p.drift}px`,
            "--particle-opacity": p.opacity,
          }}
        />
      ))}
    </div>
  );
}
