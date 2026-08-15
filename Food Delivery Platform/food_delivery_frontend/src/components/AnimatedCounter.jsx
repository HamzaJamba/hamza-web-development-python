import { useEffect, useRef, useState } from "react";

/**
 * Counts up from 0 to `value` over `duration` ms. Supports a prefix/suffix
 * (e.g. "Rs " or "%") and decimal precision.
 */
export default function AnimatedCounter({ value, duration = 900, prefix = "", suffix = "", decimals = 0 }) {
  const [display, setDisplay] = useState(0);
  const startRef = useRef(null);
  const target = Number(value) || 0;

  useEffect(() => {
    startRef.current = null;
    let raf;

    function step(timestamp) {
      if (startRef.current === null) startRef.current = timestamp;
      const progress = Math.min((timestamp - startRef.current) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
      setDisplay(target * eased);
      if (progress < 1) raf = requestAnimationFrame(step);
    }

    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [target, duration]);

  return (
    <span>
      {prefix}
      {display.toFixed(decimals)}
      {suffix}
    </span>
  );
}
