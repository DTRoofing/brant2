"use client"

import type React from "react"

import { Card, CardContent } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { CheckCircle, Clock, Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

interface ProcessingStep {
  id: string
  title: string
  description: string
  icon: React.ElementType
  status: "pending" | "processing" | "completed"
  progress: number
  duration: number
}

interface ProcessingStageProps {
  step: ProcessingStep
  isActive: boolean
  isCompleted: boolean
}

export function ProcessingStage({ step, isActive, isCompleted }: ProcessingStageProps) {
  const Icon = step.icon

  return (
    <Card
      className={cn(
        "transition-all duration-300",
        isActive && "ring-2 ring-primary/50 bg-primary/5",
        isCompleted && "bg-muted/50",
      )}
    >
      <CardContent className="p-4">
        <div className="flex items-start gap-4">
          {/* Status Icon */}
          <div
            className={cn(
              "p-2 rounded-full flex-shrink-0 transition-colors",
              step.status === "completed" && "bg-primary text-primary-foreground",
              step.status === "processing" && "bg-primary/10 text-primary",
              step.status === "pending" && "bg-muted text-muted-foreground",
            )}
          >
            {step.status === "completed" ? (
              <CheckCircle className="h-4 w-4" />
            ) : step.status === "processing" ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Clock className="h-4 w-4" />
            )}
          </div>

          {/* Content */}
          <div className="flex-1 space-y-2">
            <div className="flex items-center gap-2">
              <Icon className="h-4 w-4 text-muted-foreground" />
              <h3 className="font-semibold">{step.title}</h3>
            </div>

            <p className="text-sm text-muted-foreground">{step.description}</p>

            {step.status === "processing" && (
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span>Progress</span>
                  <span>{step.progress}%</span>
                </div>
                <Progress value={step.progress} className="h-2" />
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
