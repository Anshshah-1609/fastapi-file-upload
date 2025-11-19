import { useState, useEffect, useRef } from "react";

interface Props {
  targetNumber: number | string;
  decimalPlaces?: number; // Optional: for consistent formatting
}

export const CountUp = ({ targetNumber, decimalPlaces = 0 }: Props) => {
  const parsedTarget =
    typeof targetNumber === "string" ? parseFloat(targetNumber) : targetNumber;
  const [count, setCount] = useState(0);
  const prevTargetRef = useRef(parsedTarget);

  useEffect(() => {
    // Reset count when target changes
    if (prevTargetRef.current !== parsedTarget) {
      prevTargetRef.current = parsedTarget;
      // Use setTimeout to defer state update and avoid synchronous setState
      const timeoutId = setTimeout(() => {
    setCount(0);
      }, 0);
      return () => clearTimeout(timeoutId);
    }
  }, [parsedTarget]);

  useEffect(() => {
    if (count < parsedTarget) {
      const increment = Math.ceil(parsedTarget / 10);
      const timeout = setTimeout(() => {
        setCount((prevCount) => Math.min(prevCount + increment, parsedTarget));
      }, 100);
      return () => clearTimeout(timeout);
    }
  }, [count, parsedTarget]);

  const isGreaterThan0 = count > 0;

  const formattedCount =
    decimalPlaces > 0
      ? count.toFixed(decimalPlaces)
      : Math.round(count).toString();

  return <span>{isGreaterThan0 ? formattedCount : 0}</span>;
};
