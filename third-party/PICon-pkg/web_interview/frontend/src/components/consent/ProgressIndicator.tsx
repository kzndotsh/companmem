/**
 * Visual progress indicator for consent steps
 */

interface ProgressIndicatorProps {
  currentStep: number;
  totalSteps: number;
  label: string; // e.g., "Step 1 of 6"
}

export default function ProgressIndicator({
  currentStep,
  totalSteps,
  label,
}: ProgressIndicatorProps) {
  return (
    <div className="mb-8">
      {/* Progress label */}
      <p className="text-sm font-medium text-gray-600 text-center mb-3">
        {label}
      </p>

      {/* Progress dots */}
      <div className="flex justify-center items-center gap-2">
        {Array.from({ length: totalSteps }).map((_, index) => (
          <div
            key={index}
            className={`h-2.5 w-2.5 rounded-full transition-all duration-300 ${
              index <= currentStep
                ? 'bg-blue-600 scale-110'
                : 'bg-gray-300'
            }`}
            aria-label={`Step ${index + 1}${index <= currentStep ? ' (completed)' : ''}`}
          />
        ))}
      </div>

      {/* Progress bar */}
      <div className="mt-4 h-1 bg-gray-200 rounded-full overflow-hidden">
        <div
          className="h-full bg-blue-600 transition-all duration-500 ease-out"
          style={{ width: `${((currentStep + 1) / totalSteps) * 100}%` }}
          role="progressbar"
          aria-valuenow={currentStep + 1}
          aria-valuemin={1}
          aria-valuemax={totalSteps}
        />
      </div>
    </div>
  );
}
