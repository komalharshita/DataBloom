"use client";

import { useEffect, useRef } from "react";

type WavesProps = {
  lineColor: string;
  backgroundColor: string;
  waveSpeedX: number;
  waveSpeedY: number;
  waveAmpX: number;
  waveAmpY: number;
  friction: number;
  tension: number;
  maxCursorMove: number;
  xGap: number;
  yGap: number;
};

export default function Waves({
  lineColor,
  backgroundColor,
  waveSpeedX,
  waveSpeedY,
  waveAmpX,
  waveAmpY,
  friction,
  tension,
  maxCursorMove,
  xGap,
  yGap,
}: WavesProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const context = canvas.getContext("2d");
    if (!context) return;

    let animationFrame = 0;
    let width = 0;
    let height = 0;
    let time = 0;
    let cursorX = 0;
    let cursorY = 0;
    let targetCursorX = 0;
    let targetCursorY = 0;

    const resize = () => {
      const rect = canvas.getBoundingClientRect();
      const ratio = window.devicePixelRatio || 1;
      width = rect.width;
      height = rect.height;
      canvas.width = Math.max(1, Math.floor(width * ratio));
      canvas.height = Math.max(1, Math.floor(height * ratio));
      context.setTransform(ratio, 0, 0, ratio, 0, 0);
    };

    const moveCursor = (event: PointerEvent) => {
      const rect = canvas.getBoundingClientRect();
      targetCursorX = ((event.clientX - rect.left) / rect.width - 0.5) * maxCursorMove;
      targetCursorY = ((event.clientY - rect.top) / rect.height - 0.5) * maxCursorMove;
    };

    const draw = () => {
      time += 0.016;
      cursorX += (targetCursorX - cursorX) * tension;
      cursorY += (targetCursorY - cursorY) * tension;
      context.fillStyle = backgroundColor;
      context.fillRect(0, 0, width, height);
      context.strokeStyle = lineColor;
      context.lineWidth = 1;

      for (let y = -yGap; y <= height + yGap; y += yGap) {
        context.beginPath();
        for (let x = -xGap; x <= width + xGap; x += xGap) {
          const waveX = Math.sin(y * 0.012 + time * waveSpeedY) * waveAmpX;
          const waveY = Math.sin(x * 0.014 + time * waveSpeedX) * waveAmpY;
          const influence = Math.max(0, 1 - Math.hypot(x - width / 2, y - height / 2) / Math.max(width, height));
          const pointX = x + waveX * influence + cursorX * influence;
          const pointY = y + waveY * influence + cursorY * influence;
          if (x === -xGap) context.moveTo(pointX, pointY);
          else context.lineTo(pointX, pointY);
        }
        context.stroke();
      }

      for (let x = -xGap; x <= width + xGap; x += xGap) {
        context.beginPath();
        for (let y = -yGap; y <= height + yGap; y += yGap) {
          const waveX = Math.sin(y * 0.012 + time * waveSpeedY) * waveAmpX;
          const waveY = Math.sin(x * 0.014 + time * waveSpeedX) * waveAmpY;
          const influence = Math.max(0, 1 - Math.hypot(x - width / 2, y - height / 2) / Math.max(width, height));
          const pointX = x + waveX * influence + cursorX * influence;
          const pointY = y + waveY * influence + cursorY * influence;
          if (y === -yGap) context.moveTo(pointX, pointY);
          else context.lineTo(pointX, pointY);
        }
        context.stroke();
      }

      cursorX *= friction;
      cursorY *= friction;
      animationFrame = window.requestAnimationFrame(draw);
    };

    resize();
    window.addEventListener("resize", resize);
    window.addEventListener("pointermove", moveCursor, { passive: true });
    animationFrame = window.requestAnimationFrame(draw);

    return () => {
      window.cancelAnimationFrame(animationFrame);
      window.removeEventListener("resize", resize);
      window.removeEventListener("pointermove", moveCursor);
    };
  }, [backgroundColor, friction, lineColor, maxCursorMove, tension, waveAmpX, waveAmpY, waveSpeedX, waveSpeedY, xGap, yGap]);

  return <canvas ref={canvasRef} aria-hidden="true" />;
}
