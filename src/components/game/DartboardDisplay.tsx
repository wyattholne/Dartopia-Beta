import React, { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';

export function DartboardDisplay({ capturedFrame, lastThrow }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [highlighted, setHighlighted] = useState(false);

  const drawDartboard = (ctx: CanvasRenderingContext2D) => {
    const centerX = ctx.canvas.width / 2;
    const centerY = ctx.canvas.height / 2;
    const radius = Math.min(ctx.canvas.width, ctx.canvas.height) / 2 - 10;

    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    ctx.fillStyle = '#000';
    ctx.fill();
    ctx.strokeStyle = '#fff';
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(centerX, centerY, radius * 0.05, 0, 2 * Math.PI);
    ctx.fillStyle = '#ff0000';
    ctx.fill();

    ctx.beginPath();
    ctx.arc(centerX, centerY, radius * 0.1, 0, 2 * Math.PI);
    ctx.fillStyle = '#00ff00';
    ctx.fill();

    for (let i = 0; i < 20; i++) {
      const angle = (i * 18 - 90) * (Math.PI / 180);
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.lineTo(centerX + radius * Math.cos(angle), centerY + radius * Math.sin(angle));
      ctx.strokeStyle = '#fff';
      ctx.stroke();
    }
  };

  const drawCapturedFrame = (ctx: CanvasRenderingContext2D) => {
    if (capturedFrame) {
      const img = new Image();
      img.src = capturedFrame;
      img.onload = () => {
        ctx.drawImage(img, 0, 0, ctx.canvas.width, ctx.canvas.height);
        drawDartboard(ctx);
        if (lastThrow && highlighted) {
          const { x, y } = lastThrow;
          ctx.beginPath();
          ctx.arc(x, y, 10, 0, 2 * Math.PI);
          ctx.fillStyle = 'yellow';
          ctx.fill();
        }
      };
    } else {
      drawDartboard(ctx);
    }
  };

  React.useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        drawCapturedFrame(ctx);
      }
    }
  }, [capturedFrame, lastThrow, highlighted]);

  return (
    <Card className="w-[350px]">
      <CardHeader>
        <CardTitle>Dartboard</CardTitle>
        <CardDescription>Visual representation of the dartboard.</CardDescription>
      </CardHeader>
      <CardContent>
        <canvas ref={canvasRef} width={300} height={300} className="w-full h-[250px]" />
      </CardContent>
      <CardFooter className="flex justify-between">
        <Button variant="outline" onClick={() => setHighlighted(false)}>
          Reset
        </Button>
        <Button onClick={() => setHighlighted(true)}>
          Highlight Last Throw
        </Button>
      </CardFooter>
    </Card>
  );
}