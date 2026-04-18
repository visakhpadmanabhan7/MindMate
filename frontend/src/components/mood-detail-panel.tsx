"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { X, MessageCircle, BookOpen, Target } from "lucide-react";
import { Button } from "@/components/ui/button";

interface MoodDetail {
  id: number;
  mood: string;
  message: string;
  timestamp: string;
  source_type: string;
  source_id: number | null;
  source_content: string | null;
}

const sourceIcons = {
  chat: MessageCircle,
  journal: BookOpen,
  explicit: Target,
};

const sourceLabels = {
  chat: "From chat",
  journal: "From journal",
  explicit: "Manual entry",
};

export function MoodDetailPanel({
  detail,
  onClose,
}: {
  detail: MoodDetail;
  onClose: () => void;
}) {
  const Icon = sourceIcons[detail.source_type as keyof typeof sourceIcons] || Target;
  const label = sourceLabels[detail.source_type as keyof typeof sourceLabels] || "Unknown source";

  return (
    <Card className="border-primary/20">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Badge className="capitalize">{detail.mood}</Badge>
            <span className="text-xs text-muted-foreground flex items-center gap-1">
              <Icon className="h-3 w-3" />
              {label}
            </span>
          </div>
          <Button variant="ghost" size="icon" className="h-7 w-7" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>
        <CardTitle className="text-xs text-muted-foreground font-normal">
          {new Date(detail.timestamp).toLocaleString()}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm whitespace-pre-wrap">
          {detail.source_content || detail.message}
        </p>
      </CardContent>
    </Card>
  );
}
