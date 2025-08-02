import React, { useState, useRef, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Plus } from "lucide-react";

export function CarouselDemo() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [cards, setCards] = useState<number[]>([1]);
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const [isScrolling, setIsScrolling] = useState(false);
  const scrollTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const addCard = () => {
    setCards((prev) => [...prev, prev.length + 1]);
  };

  const closePopup = () => setActiveIndex(null);

  const cardHeight = window.innerHeight * 0.8; // from h-[80vh]
  const overlapAmount = cardHeight * 0.5; // 50% overlap

  // Scroll to bottom on first load to show the single card lower
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, []);

  // Scroll handler to detect when user stops scrolling
  const onScroll = () => {
    setIsScrolling(true);
    if (scrollTimeoutRef.current) clearTimeout(scrollTimeoutRef.current);

    scrollTimeoutRef.current = setTimeout(() => {
      setIsScrolling(false);
      snapToOverlap();
    }, 1000);
  };

  // Snap scroll to nearest overlapping card position
  const snapToOverlap = () => {
    if (!containerRef.current) return;
    const container = containerRef.current;
    const scrollTop = container.scrollTop;

    // Calculate index based on no-overlap scroll (full card height)
    const index = Math.round(scrollTop / cardHeight);

    // Scroll to position for overlap stack (index * overlapAmount)
    container.scrollTo({
      top: index * overlapAmount,
      behavior: "smooth",
    });
  };

  return (
    <>
      <div
        ref={containerRef}
        className="mx-auto h-screen overflow-y-scroll relative px-4 pt-48"
        onScroll={onScroll}
        style={{
          scrollbarWidth: "none",
          msOverflowStyle: "none",
        }}
      >
        <style>{`
          div::-webkit-scrollbar {
            display: none;
          }
        `}</style>

        {cards.map((cardNum, index) => {
          const isActive = activeIndex === index;

          return (
            <div
              key={index}
              className="relative cursor-pointer transition-all duration-300 ease-in-out"
              style={{
                marginTop: isScrolling ? 0 : index === 0 ? 0 : -overlapAmount,
                zIndex: isActive ? 100 : cards.length - index,
              }}
              onClick={() => setActiveIndex(index)}
            >
              <Card className="w-full max-w-4xl h-[80vh] mx-auto shadow-xl bg-white">
                <CardContent className="flex items-center justify-center h-full p-10">
                  <span className="text-6xl font-semibold">{cardNum}</span>
                </CardContent>
              </Card>
            </div>
          );
        })}
      </div>

      {/* Floating Add Button */}
      <button
        onClick={addCard}
        className="fixed bottom-6 right-6 bg-blue-600 hover:bg-blue-700 text-white rounded-full p-4 shadow-lg z-50"
        aria-label="Add card"
      >
        <Plus size={24} />
      </button>

      {/* Popup Modal */}
      {activeIndex !== null && (
        <div
          onClick={closePopup}
          className="fixed inset-0 flex items-center justify-center z-[9999] p-4 backdrop-blur-md bg-white/40"
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-auto p-10 relative animate-scaleFade"
          >
            <button
              onClick={closePopup}
              className="absolute top-4 right-4 text-gray-600 hover:text-gray-900 text-3xl font-bold"
            >
              &times;
            </button>
            <CardContent className="flex items-center justify-center h-full">
              <span className="text-8xl font-bold">{cards[activeIndex]}</span>
            </CardContent>
          </div>
        </div>
      )}

      <style>{`
        @keyframes scaleFade {
          0% {
            transform: scale(0.8);
            opacity: 0;
          }
          100% {
            transform: scale(1);
            opacity: 1;
          }
        }
        .animate-scaleFade {
          animation: scaleFade 0.3s ease-out forwards;
        }
      `}</style>
    </>
  );
}
