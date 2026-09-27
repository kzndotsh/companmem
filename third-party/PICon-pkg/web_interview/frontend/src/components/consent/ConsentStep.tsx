/**
 * Reusable consent step component
 */

import { ConsentStepContent } from '@/types/consent';

// Helper function to parse **bold** markers and render as <strong> elements
function renderWithBold(text: string) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={index} className="font-semibold text-gray-900">{part.slice(2, -2)}</strong>;
    }
    return part;
  });
}

interface ConsentStepProps {
  stepNumber: number;
  content: ConsentStepContent;
  isChecked: boolean;
  onCheck: (checked: boolean) => void;
}

export default function ConsentStep({
  stepNumber,
  content,
  isChecked,
  onCheck,
}: ConsentStepProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 md:p-8 max-w-3xl mx-auto">
      {/* Title */}
      <h2 className="text-2xl font-bold text-gray-800 mb-4">
        {content.title}
      </h2>

      {/* Description */}
      <p className="text-gray-700 mb-4 leading-relaxed">
        {renderWithBold(content.description)}
      </p>

      {/* Details (if provided) */}
      {content.details && content.details.length > 0 && (
        <ul className="mb-6 space-y-2">
          {content.details.map((detail, index) => (
            <li key={index} className="text-gray-600 text-sm leading-relaxed pl-4">
              {renderWithBold(detail)}
            </li>
          ))}
        </ul>
      )}

      {/* Checkbox */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <label className="flex items-start cursor-pointer group">
          <input
            type="checkbox"
            checked={isChecked}
            onChange={(e) => onCheck(e.target.checked)}
            className="mt-1 h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500 transition cursor-pointer"
          />
          <span className="ml-3 text-gray-700 font-medium group-hover:text-gray-900 transition">
            {content.checkboxLabel}
          </span>
        </label>
      </div>
    </div>
  );
}
