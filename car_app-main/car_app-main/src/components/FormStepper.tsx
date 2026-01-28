import { Check } from 'lucide-react';

interface Step {
  id: string;
  name: string;
  description?: string;
}

interface FormStepperProps {
  steps: Step[];
  currentStep: string;
}

export function FormStepper({ steps, currentStep }: FormStepperProps) {
  const currentStepIndex = steps.findIndex(step => step.id === currentStep);

  return (
    <div className="w-full py-6">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => {
          const isActive = step.id === currentStep;
          const isCompleted = index < currentStepIndex;
          
          return (
            <div key={step.id} className="flex items-center">
              <div className="flex flex-col items-center">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-colors ${
                    isCompleted
                      ? 'bg-brand-gold border-brand-gold text-black'
                      : isActive
                      ? 'border-brand-gold text-brand-gold bg-brand-gold/10'
                      : 'border-gray-600 text-gray-400'
                  }`}
                >
                  {isCompleted ? (
                    <Check className="w-6 h-6" />
                  ) : (
                    <span className="text-sm font-semibold">{index + 1}</span>
                  )}
                </div>
                <div className="mt-2 text-center">
                  <div
                    className={`text-xs font-medium ${
                      isActive ? 'text-brand-gold' : isCompleted ? 'text-brand-gold' : 'text-gray-400'
                    }`}
                  >
                    {step.name}
                  </div>
                  {step.description && (
                    <div className="text-xs text-gray-500 mt-1">
                      {step.description}
                    </div>
                  )}
                </div>
              </div>
              
              {index < steps.length - 1 && (
                <div
                  className={`h-px flex-1 mx-4 ${
                    index < currentStepIndex ? 'bg-brand-gold' : 'bg-gray-600'
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}