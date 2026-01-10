"""
Field Prompter - Displays fields and gets user input with strict validation
"""
import random
from typing import Any, List, Optional, Union


class FieldPrompter:
    """Handles prompting user for field values with strict validation"""
    
    # Class variable to track test mode
    test_mode = False
    
    @staticmethod
    def prompt_enum(field_name: str, enum_values: List[Any], nullable: bool = False, required: bool = True) -> Any:
        """
        Prompt user to select an enum value
        
        Args:
            field_name: Name/path of the field
            enum_values: List of valid enum values
            nullable: Whether null is allowed
            required: Whether field is required
        
        Returns:
            Selected enum value or None
        """
        print(f"\n=== Field: {field_name} ===")
        print("Type: enum")
        print("Options:")
        
        # Check if "unspecified" is available
        has_unspecified = "unspecified" in enum_values
        default_value = "unspecified" if has_unspecified else None
        
        options = []
        option_num = 1
        
        # Add null option if nullable
        if nullable:
            print(f"  0. (null)")
            options.append(None)
            option_num = 1
        
        # Add enum options (put unspecified first if it exists)
        other_values = [v for v in enum_values if v != "unspecified"]
        if has_unspecified:
            print(f"  {option_num}. unspecified [DEFAULT - press Enter]")
            options.append("unspecified")
            option_num += 1
        
        for enum_val in other_values:
            print(f"  {option_num}. {enum_val}")
            options.append(enum_val)
            option_num += 1
        
        # Test mode: randomly select
        if FieldPrompter.test_mode:
            if nullable and not required and random.random() < 0.2:  # 20% chance of null
                selected_value = None
            else:
                selected_value = random.choice(enum_values)
            print(f"[TEST MODE] Randomly selected: {selected_value}")
            return selected_value
        
        # Get user input
        while True:
            try:
                # Don't allow skip for fuel_economy_priority - must select null or unspecified
                allow_skip = nullable and not required and 'fuel_economy_priority' not in field_name
                
                # Use 1-based indexing if no null option, 0-based if null option exists
                if nullable:
                    # Has null option (0), so use 0-based
                    if allow_skip:
                        prompt = f"Enter selection (0-{len(options)-1}, or press Enter for default): "
                    else:
                        prompt = f"Enter selection (0-{len(options)-1}, or press Enter for default): "
                    min_selection = 0
                    max_selection = len(options) - 1
                else:
                    # No null option, use 1-based indexing
                    if default_value:
                        prompt = f"Enter selection (1-{len(options)}, or press Enter for 'unspecified'): "
                    else:
                        prompt = f"Enter selection (1-{len(options)}): "
                    min_selection = 1
                    max_selection = len(options)
                
                user_input = input(prompt).strip()
                
                # Handle Enter key - use default
                if not user_input:
                    if default_value:
                        print(f"Selected: {default_value} (default)")
                        return default_value
                    elif allow_skip:
                        return None
                    else:
                        print("Please enter a selection.")
                        continue
                
                selection = int(user_input)
                
                # Adjust selection for 1-based indexing (if no null option)
                if not nullable:
                    # User entered 1-4, but options array is 0-indexed
                    if min_selection <= selection <= max_selection:
                        selected_value = options[selection - 1]  # Convert to 0-based
                        print(f"Selected: {selected_value}")
                        return selected_value
                    else:
                        print(f"Invalid selection. Please choose {min_selection}-{max_selection}.")
                else:
                    # Has null option, use 0-based indexing
                    if 0 <= selection < len(options):
                        selected_value = options[selection]
                        print(f"Selected: {selected_value}")
                        return selected_value
                    else:
                        print(f"Invalid selection. Please choose 0-{len(options)-1}.")
            
            except ValueError:
                print("Please enter a valid number.")
    
    @staticmethod
    def prompt_array_enum(field_name: str, enum_values: List[Any], nullable: bool = False, required: bool = True) -> Optional[List[Any]]:
        """
        Prompt user to select multiple enum values (for arrays)
        
        Args:
            field_name: Name/path of the field
            enum_values: List of valid enum values
            nullable: Whether null is allowed
            required: Whether field is required
        
        Returns:
            List of selected enum values, or None if null
        """
        print(f"\n=== Field: {field_name} ===")
        print("Type: array of enum")
        
        # Check if "unspecified" is available
        has_unspecified = "unspecified" in enum_values
        default_value = ["unspecified"] if has_unspecified else []
        
        print("Select one or more options (comma-separated numbers, 'done' when finished, or press Enter for default):")
        
        options = []
        option_num = 1
        
        # Add enum options (put unspecified first if it exists)
        other_values = [v for v in enum_values if v != "unspecified"]
        if has_unspecified:
            print(f"  {option_num}. unspecified [DEFAULT - press Enter]")
            options.append("unspecified")
            option_num += 1
        
        for enum_val in other_values:
            print(f"  {option_num}. {enum_val}")
            options.append(enum_val)
            option_num += 1
        
        # Test mode: randomly select 1-3 values
        if FieldPrompter.test_mode:
            if required or random.random() > 0.1:  # 90% chance of selecting something if not required
                num_selections = random.randint(1, min(3, len(enum_values)))
                selected_values = random.sample(enum_values, num_selections)
            else:
                selected_values = []
            print(f"[TEST MODE] Randomly selected: {selected_values}")
            return selected_values
        
        selections = []
        
        # Get user input
        while True:
            try:
                if default_value:
                    prompt = f"Enter selection(s) (or press Enter for ['unspecified']): "
                else:
                    prompt = f"Enter selection(s): "
                
                user_input = input(prompt).strip().lower()
                
                # Handle Enter key - use default
                if not user_input:
                    if default_value:
                        print(f"Selected: {default_value} (default)")
                        return default_value
                    elif not required:
                        print("Selected: [] (empty array)")
                        return []
                    else:
                        print("This field is required. Please select at least one option.")
                        continue
                
                if user_input == 'done':
                    if required and len(selections) == 0:
                        print("This field is required. Please select at least one option.")
                        continue
                    break
                
                # Parse comma-separated numbers
                selected_nums = [int(x.strip()) for x in user_input.split(',')]
                
                # Validate all selections
                valid = True
                for num in selected_nums:
                    if not (1 <= num <= len(options)):
                        print(f"Invalid selection: {num}. Please choose 1-{len(options)}.")
                        valid = False
                        break
                
                if not valid:
                    continue
                
                # Add selected values (avoid duplicates)
                for num in selected_nums:
                    value = options[num - 1]
                    if value not in selections:
                        selections.append(value)
                        print(f"Added: {value}")
            
            except ValueError:
                print("Please enter valid numbers separated by commas, 'done', or press Enter for default.")
        
        print(f"Selected: {selections}")
        return selections
    
    @staticmethod
    def prompt_array_string(field_name: str, nullable: bool = False, required: bool = True) -> Optional[List[str]]:
        """
        Prompt user for multiple string values (comma-separated)
        
        Args:
            field_name: Name/path of the field
            nullable: Whether null is allowed
            required: Whether field is required
        
        Returns:
            List of string values, or None if null
        """
        print(f"\n=== Field: {field_name} ===")
        print("Type: array of strings")
        print("Enter comma-separated values (e.g., 'Toyota, Honda' or 'Camry, Accord')")
        
        default_value = ["unspecified"]
        
        # Test mode: return random string array
        if FieldPrompter.test_mode:
            if field_name == 'make':
                makes = ['Toyota', 'Honda', 'Ford', 'Chevrolet', 'BMW', 'Mercedes-Benz']
                num_selections = random.randint(1, 2)
                selected_values = random.sample(makes, min(num_selections, len(makes)))
            elif field_name == 'model':
                models = ['Camry', 'Accord', 'F-150', 'Silverado', '3 Series', 'C-Class']
                num_selections = random.randint(1, 2)
                selected_values = random.sample(models, min(num_selections, len(models)))
            else:
                num_selections = random.randint(1, 2)
                selected_values = [f"value_{i}" for i in range(1, num_selections + 1)]
            print(f"[TEST MODE] Randomly selected: {selected_values}")
            return selected_values
        
        while True:
            try:
                if default_value:
                    prompt = f"Enter comma-separated {field_name} values (or press Enter for ['unspecified']): "
                else:
                    prompt = f"Enter comma-separated {field_name} values: "
                
                user_input = input(prompt).strip()
                
                # Handle Enter key - use default
                if not user_input:
                    if default_value:
                        print(f"Selected: {default_value} (default)")
                        return default_value
                    elif not required:
                        print("Selected: [] (empty array)")
                        return []
                    else:
                        print("This field is required. Please enter at least one value.")
                        continue
                
                # Handle "unspecified" as single value
                if user_input.lower() == 'unspecified':
                    print("Selected: ['unspecified']")
                    return ["unspecified"]
                
                # Split by comma and strip whitespace, filter out empty strings
                values = [v.strip() for v in user_input.split(',') if v.strip()]
                
                if not values:
                    print("No valid values entered. Please enter at least one value, or press Enter for default.")
                    continue
                
                if required and len(values) == 0:
                    print("This field is required. Please enter at least one value.")
                    continue
                
                print(f"Selected: {values}")
                return values
            
            except Exception as e:
                print(f"Error: {e}. Please enter comma-separated values.")
    
    @staticmethod
    def prompt_number(field_name: str, nullable: bool = False, required: bool = True) -> Optional[Union[int, float]]:
        """
        Prompt user for a number
        
        Args:
            field_name: Name/path of the field
            nullable: Whether null is allowed
            required: Whether field is required
        
        Returns:
            Number value or None
        """
        print(f"\n=== Field: {field_name} ===")
        print("Type: number")
        
        # Test mode: return random number or null
        if FieldPrompter.test_mode:
            if nullable and not required and random.random() < 0.3:  # 30% chance of null
                print("[TEST MODE] Randomly selected: null")
                return None
            else:
                value = random.randint(1, 100)  # Random integer 1-100
                print(f"[TEST MODE] Randomly selected: {value}")
                return value
        
        while True:
            try:
                # Check if this is a budget/year/radius field that should use unspecified
                is_budget_year_radius = any(x in field_name for x in ['budget.min', 'budget.max', 'year.min', 'year.max', 'radius_miles'])
                
                if is_budget_year_radius:
                    prompt = f"Enter value (or press Enter for 'unspecified'): "
                elif nullable and not required:
                    prompt = f"Enter value (or 'null', or press Enter to skip): "
                else:
                    prompt = f"Enter value: "
                
                user_input = input(prompt).strip()
                
                # Handle Enter key - default to unspecified for budget/year/radius fields
                if not user_input:
                    if is_budget_year_radius:
                        print("Entered: unspecified (default)")
                        return "unspecified"
                    elif nullable and not required:
                        return None
                    else:
                        print("Please enter a value.")
                        continue
                
                # Handle unspecified for budget/year/radius fields
                if user_input.lower() == 'unspecified' and is_budget_year_radius:
                    print("Entered: unspecified")
                    return "unspecified"
                
                # Handle null
                if user_input.lower() == 'null':
                    if nullable:
                        return None
                    else:
                        print("This field does not allow null values. Use 'unspecified' instead.")
                        continue
                
                # Try integer first, then float
                try:
                    value = int(user_input)
                except ValueError:
                    value = float(user_input)
                
                print(f"Entered: {value}")
                return value
            
            except ValueError:
                if is_budget_year_radius:
                    print("Please enter a valid number, 'unspecified', or press Enter for default.")
                else:
                    print("Please enter a valid number.")
    
    @staticmethod
    def prompt_string(field_name: str, nullable: bool = False, required: bool = True) -> Optional[str]:
        """
        Prompt user for a string
        
        Args:
            field_name: Name/path of the field
            nullable: Whether null is allowed
            required: Whether field is required
        
        Returns:
            String value or None
        """
        print(f"\n=== Field: {field_name} ===")
        print("Type: string")
        
        # Special handling for trim
        is_trim = field_name == 'trim'
        
        # Test mode: return placeholder string or null
        if FieldPrompter.test_mode:
            if is_trim:
                if random.random() < 0.3:  # 30% chance of unspecified
                    value = "unspecified"
                else:
                    trims = ['Base', 'LE', 'XLE', 'Sport', 'Limited', 'Premium']
                    value = random.choice(trims)
            elif nullable and not required and random.random() < 0.2:  # 20% chance of null
                print("[TEST MODE] Randomly selected: null")
                return None
            else:
                value = f"test_value_{field_name.replace('.', '_')}"
            print(f"[TEST MODE] Randomly selected: {value}")
            return value
        
        while True:
            # Special handling for trim - string with unspecified option
            if is_trim:
                prompt = f"Enter trim (text/string, or press Enter for 'unspecified'): "
                user_input = input(prompt).strip()
                
                # Handle Enter key - default to unspecified
                if not user_input:
                    print("Entered: unspecified (default)")
                    return "unspecified"
                
                if user_input.lower() == 'unspecified':
                    print("Entered: unspecified")
                    return "unspecified"
                
                print(f"Entered: {user_input}")
                return user_input
            
            # Don't allow skip for city and state_region - must enter value or unspecified
            allow_skip = nullable and not required and 'city' not in field_name and 'state_region' not in field_name
            
            # String fields support unspecified as default (city, state_region, radius_miles, query_text, trim, etc.)
            supports_unspecified = True
            
            if supports_unspecified:
                prompt = f"Enter value (or press Enter for 'unspecified'): "
            elif allow_skip:
                prompt = f"Enter value (or 'null', or press Enter to skip): "
            elif nullable:
                prompt = f"Enter value (or 'null'): "
            else:
                prompt = f"Enter value: "
            
            user_input = input(prompt).strip()
            
            # Handle Enter key - default to unspecified for fields that support it
            if not user_input:
                if supports_unspecified:
                    print("Entered: unspecified (default)")
                    return "unspecified"
                elif allow_skip:
                    return None
                elif required:
                    print("This field is required. Please enter a value or 'unspecified'.")
                    continue
                else:
                    return None
            
            # Handle unspecified (preferred over null)
            if user_input.lower() == 'unspecified':
                print("Entered: unspecified")
                return "unspecified"
            
            # Handle null (for backward compatibility, but we're moving away from this)
            if user_input.lower() == 'null':
                if nullable:
                    return None
                else:
                    print("This field does not allow null values. Use 'unspecified' instead.")
                    continue
            
            # Required field must have value
            if required and not user_input:
                print("This field is required. Please enter a value or 'unspecified'.")
                continue
            
            print(f"Entered: {user_input}")
            return user_input
    
    @staticmethod
    def prompt_integer_or_unspecified(field_name: str, required: bool = True) -> Union[int, str]:
        """
        Prompt user for an integer or "unspecified"
        
        Args:
            field_name: Name/path of the field
            required: Whether field is required
        
        Returns:
            Integer value or "unspecified" string
        """
        print(f"\n=== Field: {field_name} ===")
        
        # Special handling for currency
        if 'currency' in field_name:
            print("Type: currency (integer, ISO 4217 code)")
            print("Format: Enter ISO 4217 numeric code (e.g., 840 for USD, 978 for EUR)")
            print("Options:")
            print("  Press Enter for default: 840 (USD)")
            print("  Enter ISO 4217 code (integer)")
            print("  Enter 'unspecified' for unspecified")
        elif 'budget.min' in field_name or 'budget.max' in field_name:
            print("Type: number or unspecified")
            print("Enter budget amount (number, can include decimals)")
            print("Options:")
            print("  Enter a number value")
            print("  Enter 'unspecified' for unspecified")
        elif 'year.min' in field_name or 'year.max' in field_name:
            print("Type: integer or unspecified")
            print("Enter year (integer)")
            print("Options:")
            print("  Enter a year value")
            print("  Enter 'unspecified' for unspecified")
        elif 'radius_miles' in field_name:
            print("Type: number or unspecified")
            print("Enter radius in miles (number, can include decimals)")
            print("Options:")
            print("  Enter a number value")
            print("  Enter 'unspecified' for unspecified")
        elif 'kid_count' in field_name or 'pet_count' in field_name:
            print("Type: integer or unspecified")
            print("Note: 0 means no kids/pets (a valid value), not unspecified")
            print("Options:")
            print("  Enter an integer (0 or higher) for the count")
            print("  Enter 'unspecified' if the count was not mentioned")
        elif 'number_of_owners' in field_name:
            print("Type: integer or unspecified")
            print("Enter number of owners (integer, 0 or higher)")
            print("Options:")
            print("  Enter an integer (0 or higher) for the number of owners")
            print("  Enter 'unspecified' for unspecified")
        else:
            print("Type: integer or unspecified")
            if 'seating_capacity' in field_name:
                print("Enter minimum seating capacity (integer, minimum: 1)")
            print("Options:")
            print("  Enter an integer value")
            print("  Enter 'unspecified' for unspecified")
        
        # Test mode: randomly select integer or unspecified
        if FieldPrompter.test_mode:
            if random.random() < 0.2:  # 20% chance of unspecified
                print("[TEST MODE] Randomly selected: unspecified")
                return "unspecified"
            else:
                if 'currency' in field_name:
                    # Default to 840 (USD) in test mode
                    value = 840
                elif 'kid_count' in field_name or 'pet_count' in field_name:
                    value = random.randint(0, 5)  # 0-5 for kids/pets
                elif 'number_of_owners' in field_name:
                    value = random.randint(0, 5)  # 0-5 owners
                else:
                    value = random.randint(1, 10)
                print(f"[TEST MODE] Randomly selected: {value}")
                return value
        
        while True:
            try:
                if 'currency' in field_name:
                    prompt = f"Enter ISO 4217 code (or press Enter for 840/USD): "
                elif 'kid_count' in field_name or 'pet_count' in field_name:
                    prompt = f"Enter count (0 or higher, or press Enter for 'unspecified'): "
                elif 'number_of_owners' in field_name:
                    prompt = f"Enter number of owners (0 or higher, or press Enter for 'unspecified'): "
                else:
                    prompt = f"Enter value (or press Enter for 'unspecified'): "
                
                user_input = input(prompt).strip().lower()
                
                # Handle Enter key - default based on field type
                if not user_input:
                    if 'currency' in field_name:
                        print("Selected: 840 (USD - default)")
                        return 840
                    else:
                        print("Selected: unspecified (default)")
                        return "unspecified"
                
                if user_input == 'unspecified':
                    print("Selected: unspecified")
                    return "unspecified"
                
                # Parse as number (remove any commas user might have entered)
                value_str = user_input.replace(',', '').strip()
                
                # Try integer first, then float (for budget fields which can be decimals)
                try:
                    value = int(value_str)
                except ValueError:
                    value = float(value_str)
                
                # Validate minimums
                if 'seating_capacity' in field_name and value < 1:
                    print("Error: Minimum seating capacity must be at least 1.")
                    continue
                if ('kid_count' in field_name or 'pet_count' in field_name) and value < 0:
                    print("Error: Count cannot be negative.")
                    continue
                if 'number_of_owners' in field_name and value < 0:
                    print("Error: Number of owners cannot be negative.")
                    continue
                
                print(f"Entered: {value}")
                return value
            
            except ValueError:
                if 'kid_count' in field_name or 'pet_count' in field_name or 'number_of_owners' in field_name:
                    print("Please enter a valid integer (0 or higher) or 'unspecified'.")
                else:
                    print("Please enter a valid integer (no commas) or 'unspecified'.")
    
    @staticmethod
    def prompt_boolean(field_name: str, nullable: bool = False, required: bool = True) -> Optional[Union[bool, str]]:
        """
        Prompt user for a boolean or "unspecified"
        
        Args:
            field_name: Name/path of the field
            nullable: Whether null is allowed
            required: Whether field is required
        
        Returns:
            Boolean value, "unspecified" string, or None
        """
        # Check if this field supports "unspecified" (boolean_with_unspecified type)
        supports_unspecified = any(x in field_name for x in ['wants_hatch_access', 'wants_fold_flat_seats', 'strict_max'])
        
        print(f"\n=== Field: {field_name} ===")
        print("Type: boolean")
        print("Options:")
        
        options = []
        option_num = 1
        
        if supports_unspecified:
            print(f"  {option_num}. unspecified [DEFAULT - press Enter]")
            options.append("unspecified")
            option_num += 1
        
        print(f"  {option_num}. true")
        options.append(True)
        option_num += 1
        
        print(f"  {option_num}. false")
        options.append(False)
        option_num += 1
        
        if nullable:
            print(f"  0. (null)")
        
        # Test mode: randomly select
        if FieldPrompter.test_mode:
            if supports_unspecified and random.random() < 0.3:  # 30% chance of unspecified
                print("[TEST MODE] Randomly selected: unspecified")
                return "unspecified"
            elif nullable and not required and random.random() < 0.2:  # 20% chance of null
                print("[TEST MODE] Randomly selected: null")
                return None
            else:
                value = random.choice([True, False])
                print(f"[TEST MODE] Randomly selected: {value}")
                return value
        
        while True:
            try:
                if supports_unspecified:
                    prompt = f"Enter selection (1-{len(options)}, or press Enter for 'unspecified'): "
                elif nullable and not required:
                    prompt = f"Enter selection (0-2, or press Enter to skip): "
                else:
                    prompt = f"Enter selection (1-2): "
                
                user_input = input(prompt).strip()
                
                # Handle Enter key - default to unspecified if supported
                if not user_input:
                    if supports_unspecified:
                        print("Selected: unspecified (default)")
                        return "unspecified"
                    elif nullable and not required:
                        return None
                    else:
                        print("Please enter a selection.")
                        continue
                
                selection = int(user_input)
                
                # Handle null option
                if nullable and selection == 0:
                    return None
                
                # Adjust for 1-based indexing
                if 1 <= selection <= len(options):
                    selected_value = options[selection - 1]
                    print(f"Selected: {selected_value}")
                    return selected_value
                else:
                    if supports_unspecified:
                        print(f"Invalid selection. Please choose 1-{len(options)}, or press Enter for default.")
                    else:
                        print("Invalid selection. Please choose 1-2 (or 0 for null).")
            
            except ValueError:
                print("Please enter a valid number.")


