"use client";

import { Button } from "@/components/ui/button";

interface PaginationProps {
  total: number;
  page: number;
  onPageChange: (page: number) => void;
}

export function Pagination({ total, page, onPageChange }: PaginationProps) {
  return (
    <div className="flex items-center space-x-2">
      <Button
        variant="outline"
        size="sm"
        onClick={() => onPageChange(page - 1)}
        disabled={page === 1}
      >
        Previous
      </Button>
      {Array.from({ length: total }).map((_, index) => (
        <Button
          key={index}
          variant={page === index + 1 ? "default" : "outline"}
          size="sm"
          onClick={() => onPageChange(index + 1)}
        >
          {index + 1}
        </Button>
      ))}
      <Button
        variant="outline"
        size="sm"
        onClick={() => onPageChange(page + 1)}
        disabled={page === total}
      >
        Next
      </Button>
    </div>
  );
}
