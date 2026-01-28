import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, Search } from 'lucide-react';

interface SearchableDropdownProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
  displayValue: (item: T) => string;
  onSelect: (item: T) => void;
  placeholder?: string;
  error?: string;
  selectedItem?: T | null;
}

export function SearchableDropdown<T>({
  items,
  renderItem,
  displayValue,
  onSelect,
  placeholder = "Search and select...",
  error,
  selectedItem,
}: SearchableDropdownProps<T>) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [displayText, setDisplayText] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Update display text when selectedItem changes
  useEffect(() => {
    if (selectedItem) {
      setDisplayText(displayValue(selectedItem));
      setSearchTerm('');
    } else {
      setDisplayText('');
      setSearchTerm('');
    }
  }, [selectedItem, displayValue]);

  // Filter items based on search term
  const filteredItems = items.filter(item =>
    displayValue(item).toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Handle clicking outside to close dropdown
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        if (selectedItem) {
          setDisplayText(displayValue(selectedItem));
          setSearchTerm('');
        } else {
          setDisplayText('');
          setSearchTerm('');
        }
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [selectedItem, displayValue]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
    setDisplayText(e.target.value);
    setIsOpen(true);
  };

  const handleItemSelect = (item: T) => {
    onSelect(item);
    setIsOpen(false);
    setSearchTerm('');
    setDisplayText(displayValue(item));
  };

  const handleInputFocus = () => {
    setIsOpen(true);
    if (selectedItem) {
      setDisplayText('');
      setSearchTerm('');
    }
  };

  return (
    <div ref={dropdownRef} className="relative">
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={isOpen ? searchTerm : displayText}
          onChange={handleInputChange}
          onFocus={handleInputFocus}
          placeholder={placeholder}
          className={`w-full px-3 py-2 pr-10 border rounded-md bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent ${
            error ? 'border-red-500' : 'border-gray-600'
          }`}
        />
        <div className="absolute inset-y-0 right-0 flex items-center px-3 pointer-events-none">
          {isOpen ? (
            <Search className="h-4 w-4 text-gray-400" />
          ) : (
            <ChevronDown className="h-4 w-4 text-gray-400" />
          )}
        </div>
      </div>

      {error && (
        <p className="text-red-400 text-xs mt-1">{error}</p>
      )}

      {isOpen && (
        <div className="absolute z-50 w-full mt-1 bg-gray-800 border border-gray-600 rounded-md shadow-lg max-h-80 overflow-y-auto">
          {filteredItems.length === 0 ? (
            <div className="px-4 py-3 text-gray-400 text-sm">
              No vehicles found matching "{searchTerm}"
            </div>
          ) : (
            <div className="py-1">
              {filteredItems.map((item, index) => (
                <div
                  key={index}
                  onClick={() => handleItemSelect(item)}
                  className="cursor-pointer hover:bg-gray-700 transition-colors"
                >
                  {renderItem(item)}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}