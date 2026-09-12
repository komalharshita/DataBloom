"use client";

import { useEffect, useRef } from "react";

const INTERACTIVE_SELECTOR = "a, button, input, textarea, select, label, [role=button], .sample-card, .drop-zone";

export default function CustomCursor() {
  const cursorRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const finePointer = window.matchMedia("(pointer: fine) and (hover: hover)");
    if (!finePointer.matches) return;

    const cursor = cursorRef.current;
    if (!cursor) return;

    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    const root = document.documentElement;
    let currentX = -100;
    let currentY = -100;
    let targetX = currentX;
    let targetY = currentY;
    let animationFrame = 0;

    root.classList.add("has-custom-cursor");

    const render = () => {
      if (reducedMotion.matches) {
        currentX = targetX;
        currentY = targetY;
      } else {
        currentX += (targetX - currentX) * 0.24;
        currentY += (targetY - currentY) * 0.24;
      }
      cursor.style.transform = `translate3d(${currentX}px, ${currentY}px, 0)`;
      animationFrame = window.requestAnimationFrame(render);
    };

    const move = (event: PointerEvent) => {
      targetX = event.clientX;
      targetY = event.clientY;
      const interactive = (event.target as Element | null)?.closest(INTERACTIVE_SELECTOR);
      cursor.dataset.hover = interactive ? "true" : "false";
    };

    const leave = () => {
      cursor.dataset.visible = "false";
    };

    const enter = () => {
      cursor.dataset.visible = "true";
    };

    document.addEventListener("pointermove", move, { passive: true });
    document.addEventListener("pointerleave", leave);
    document.addEventListener("pointerenter", enter);
    animationFrame = window.requestAnimationFrame(render);

    return () => {
      window.cancelAnimationFrame(animationFrame);
      document.removeEventListener("pointermove", move);
      document.removeEventListener("pointerleave", leave);
      document.removeEventListener("pointerenter", enter);
      root.classList.remove("has-custom-cursor");
    };
  }, []);

  return <div ref={cursorRef} className="custom-cursor" data-visible="false" data-hover="false" aria-hidden="true"><span /></div>;
}
