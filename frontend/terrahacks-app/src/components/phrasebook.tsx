import React, { useRef } from "react";
import { Card, CardContent } from "@/components/ui/card";

export default function VerticalOverlapCarousel() {
  const containerRef = useRef<HTMLDivElement>(null);

  // Scroll the clicked card into view smoothly inside container
  const scrollToCard = (index: number) => {
    if (!containerRef.current) return;
    const container = containerRef.current;
    const card = container.children[index] as HTMLElement;
    if (!card) return;

    // Scroll so card's top aligns with container's top, smoothly
    container.scrollTo({
      top: card.offsetTop,
      behavior: "smooth",
    });
  };

  return (
    <div
      ref={containerRef}
      className="max-w-xs mx-auto h-96 overflow-y-scroll"
      style={{ scrollbarWidth: "thin" }}
    >
      {Array.from({ length: 7 }).map((_, index) => (
        <div
          key={index}
          className="relative cursor-pointer"
          style={{
            marginTop: index === 0 ? 0 : -40,
            zIndex: 10 - index,
          }}
          onClick={() => scrollToCard(index)}
          aria-label={`Scroll to card ${index + 1}`}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              scrollToCard(index);
            }
          }}
        >
          <Card className="shadow-lg">
            <CardContent className="flex aspect-square items-center justify-center p-6 bg-white">
              <span className="text-4xl font-semibold">{index + 1}</span>
            </CardContent>
          </Card>
        </div>
      ))}
    </div>
  );
}
