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
        
        options = []
        option_num = 1
        
        # Add null option if nullable
        if nullable:
            print(f"  0. (null)")
            options.append(None)
            option_num = 1
        
        # Add enum options
        for enum_val in enum_values:
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
                
                if allow_skip:
                    prompt = f"Enter selection (0-{len(options)-1}, or press Enter to skip): "
                else:
                    prompt = f"Enter selection (0-{len(options)-1}): "
                
                user_input = input(prompt).strip()
                
                # Handle skip for optional nullable (but not for fuel_economy_priority)
                if not user_input and allow_skip:
                    return None
                
                selection = int(user_input)
                
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
        print("Select one or more options (comma-separated numbers, or 'done' when finished):")
        
        options = []
        option_num = 1
        
        # Add enum options
        for enum_val in enum_values:
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
                prompt = f"Enter selection(s): "
                
                user_input = input(prompt).strip().lower()
                
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
                print("Please enter valid numbers separated by commas, or 'done'.")
        
        print(f"Selected: {selections}")
        return selections
    
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
                if nullable and not required:
                    prompt = f"Enter value (or 'null'): "
                else:
                    prompt = f"Enter value: "
                
                user_input = input(prompt).strip()
                
                # Handle null
                if user_input.lower() == 'null':
                    if nullable:
                        return None
                    else:
                        print("This field does not allow null values.")
                        continue
                
                # Handle skip for optional nullable
                if not user_input and nullable and not required:
                    return None
                
                # Try integer first, then float
                try:
                    value = int(user_input)
                except ValueError:
                    value = float(user_input)
                
                print(f"Entered: {value}")
                return value
            
            except ValueError:
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
        
        # Test mode: return placeholder string or null
        if FieldPrompter.test_mode:
            if nullable and not required and random.random() < 0.2:  # 20% chance of null
                print("[TEST MODE] Randomly selected: null")
                return None
            else:
                value = f"test_value_{field_name.replace('.', '_')}"
                print(f"[TEST MODE] Randomly selected: {value}")
                return value
        
        while True:
            # Don't allow skip for city and state_region - must enter value, null, or unspecified
            allow_skip = nullable and not required and 'city' not in field_name and 'state_region' not in field_name
            
            if allow_skip:
                prompt = f"Enter value (or 'null', or press Enter to skip): "
            elif nullable:
                prompt = f"Enter value (or 'null'): "
            else:
                prompt = f"Enter value: "
            
            user_input = input(prompt).strip()
            
            # Handle null
            if user_input.lower() == 'null':
                if nullable:
                    return None
                else:
                    print("This field does not allow null values.")
                    continue
            
            # Handle skip for optional nullable (but not for city/state_region)
            if not user_input and allow_skip:
                return None
            
            # Required field must have value
            if required and not user_input:
                print("This field is required. Please enter a value.")
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
            print("Type: currency (integer, no commas)")
            print("Format: Enter numerical value with no commas (e.g., 50000 for 50k, 1200, 200000)")
            print("Options:")
            print("  0. unspecified")
        else:
            print("Type: integer or unspecified")
            print("Options:")
            print("  0. unspecified")
        
        # Test mode: randomly select integer or unspecified
        if FieldPrompter.test_mode:
            if random.random() < 0.2:  # 20% chance of unspecified
                print("[TEST MODE] Randomly selected: unspecified")
                return "unspecified"
            else:
                value = random.randint(1000, 100000)
                print(f"[TEST MODE] Randomly selected: {value}")
                return value
        
        while True:
            try:
                prompt = f"Enter value (or 0 for unspecified): "
                user_input = input(prompt).strip()
                
                if user_input == '0':
                    print("Selected: unspecified")
                    return "unspecified"
                
                # Parse as integer (remove any commas user might have entered)
                value_str = user_input.replace(',', '').strip()
                value = int(value_str)
                
                print(f"Entered: {value}")
                return value
            
            except ValueError:
                print("Please enter a valid integer (no commas) or 0 for unspecified.")
    
    @staticmethod
    def prompt_boolean(field_name: str, nullable: bool = False, required: bool = True) -> Optional[bool]:
        """
        Prompt user for a boolean
        
        Args:
            field_name: Name/path of the field
            nullable: Whether null is allowed
            required: Whether field is required
        
        Returns:
            Boolean value or None
        """
        print(f"\n=== Field: {field_name} ===")
        print("Type: boolean")
        print("Options:")
        print("  1. true")
        print("  2. false")
        
        if nullable:
            print("  0. (null)")
        
        # Test mode: randomly select
        if FieldPrompter.test_mode:
            if nullable and not required and random.random() < 0.2:  # 20% chance of null
                print("[TEST MODE] Randomly selected: null")
                return None
            else:
                value = random.choice([True, False])
                print(f"[TEST MODE] Randomly selected: {value}")
                return value
        
        while True:
            try:
                if nullable and not required:
                    prompt = f"Enter selection (0-2, or press Enter to skip): "
                else:
                    prompt = f"Enter selection (1-2): "
                
                user_input = input(prompt).strip()
                
                # Handle skip for optional nullable
                if not user_input and nullable and not required:
                    return None
                
                selection = int(user_input)
                
                if nullable and selection == 0:
                    return None
                elif selection == 1:
                    print("Selected: true")
                    return True
                elif selection == 2:
                    print("Selected: false")
                    return False
                else:
                    print("Invalid selection. Please choose 1-2 (or 0 for null).")
            
            except ValueError:
                print("Please enter a valid number.")


