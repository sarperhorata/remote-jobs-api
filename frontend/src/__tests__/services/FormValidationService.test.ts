describe('Form Validation Service Tests', () => {
  
  describe('Email Validation', () => {
    const validateEmail = (email: string): { isValid: boolean; error?: string } => {
      if (!email) {
        return { isValid: false, error: 'Email is required' };
      }
      
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        return { isValid: false, error: 'Please enter a valid email address' };
      }
      
      if (email.length > 254) {
        return { isValid: false, error: 'Email address is too long' };
      }
      
      return { isValid: true };
    };

    test('should validate correct email addresses', () => {
      const validEmails = [
        'test@example.com',
        'user.name@domain.co.uk',
        'user+tag@example.org',
        'test123@test-domain.com'
      ];

      validEmails.forEach(email => {
        const result = validateEmail(email);
        expect(result.isValid).toBe(true);
        expect(result.error).toBeUndefined();
      });
    });

    test('should reject invalid email addresses', () => {
      const invalidEmails = [
        '',
        'invalid-email',
        '@example.com',
        'test@',
        'test.example.com',
        'test@.com',
        'test@domain.',
        'test space@example.com'
      ];

      invalidEmails.forEach(email => {
        const result = validateEmail(email);
        expect(result.isValid).toBe(false);
        expect(result.error).toBeDefined();
      });
    });

    test('should reject too long email addresses', () => {
      const longEmail = 'a'.repeat(250) + '@example.com';
      const result = validateEmail(longEmail);
      
      expect(result.isValid).toBe(false);
      expect(result.error).toBe('Email address is too long');
    });
  });

  describe('Password Validation', () => {
    const validatePassword = (password: string): { isValid: boolean; errors: string[] } => {
      const errors: string[] = [];
      
      if (!password) {
        errors.push('Password is required');
        return { isValid: false, errors };
      }
      
      if (password.length < 8) {
        errors.push('Password must be at least 8 characters long');
      }
      
      if (password.length > 128) {
        errors.push('Password must be less than 128 characters');
      }
      
      if (!/[a-z]/.test(password)) {
        errors.push('Password must contain at least one lowercase letter');
      }
      
      if (!/[A-Z]/.test(password)) {
        errors.push('Password must contain at least one uppercase letter');
      }
      
      if (!/\d/.test(password)) {
        errors.push('Password must contain at least one number');
      }
      
      if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
        errors.push('Password must contain at least one special character');
      }
      
      return { isValid: errors.length === 0, errors };
    };

    test('should validate strong passwords', () => {
      const strongPasswords = [
        'MyStr0ngP@ssw0rd',
        'C0mpl3x!P@ssw0rd',
        'S3cur3P@ss123!',
        'V3ryStr0ng#Password'
      ];

      strongPasswords.forEach(password => {
        const result = validatePassword(password);
        expect(result.isValid).toBe(true);
        expect(result.errors).toHaveLength(0);
      });
    });

    test('should reject weak passwords', () => {
      const weakPasswords = [
        '',
        '123456',
        'password',
        'PASSWORD',
        'Password',
        'Password1',
        'pass123!',
        'PASS123!'
      ];

      weakPasswords.forEach(password => {
        const result = validatePassword(password);
        expect(result.isValid).toBe(false);
        expect(result.errors.length).toBeGreaterThan(0);
      });
    });

    test('should provide specific error messages', () => {
      const result = validatePassword('weak');
      
      expect(result.errors).toContain('Password must be at least 8 characters long');
      expect(result.errors).toContain('Password must contain at least one uppercase letter');
      expect(result.errors).toContain('Password must contain at least one number');
      expect(result.errors).toContain('Password must contain at least one special character');
    });
  });

  describe('Form Field Validation', () => {
    const validateField = (fieldName: string, value: any, rules: any): { isValid: boolean; error?: string } => {
      const fieldRules = rules[fieldName];
      if (!fieldRules) return { isValid: true };
      
      // Required validation
      if (fieldRules.required && (!value || (typeof value === 'string' && value.trim() === ''))) {
        return { isValid: false, error: `${fieldName} is required` };
      }
      
      // Skip other validations if field is empty and not required
      if (!value || (typeof value === 'string' && value.trim() === '')) {
        return { isValid: true };
      }
      
      // Length validation
      if (fieldRules.minLength && value.length < fieldRules.minLength) {
        return { isValid: false, error: `${fieldName} must be at least ${fieldRules.minLength} characters` };
      }
      
      if (fieldRules.maxLength && value.length > fieldRules.maxLength) {
        return { isValid: false, error: `${fieldName} must be no more than ${fieldRules.maxLength} characters` };
      }
      
      // Pattern validation
      if (fieldRules.pattern && !fieldRules.pattern.test(value)) {
        return { isValid: false, error: fieldRules.patternError || `${fieldName} format is invalid` };
      }
      
      // Custom validation
      if (fieldRules.custom && typeof fieldRules.custom === 'function') {
        const customResult = fieldRules.custom(value);
        if (!customResult.isValid) {
          return customResult;
        }
      }
      
      return { isValid: true };
    };

    const validateForm = (formData: any, rules: any): { isValid: boolean; errors: { [key: string]: string } } => {
      const errors: { [key: string]: string } = {};
      
      for (const fieldName in rules) {
        const result = validateField(fieldName, formData[fieldName], rules);
        if (!result.isValid) {
          errors[fieldName] = result.error!;
        }
      }
      
      return { isValid: Object.keys(errors).length === 0, errors };
    };

    test('should validate required fields', () => {
      const rules = {
        name: { required: true },
        email: { required: true },
        phone: { required: false }
      };
      
      const validData = { name: 'John Doe', email: 'john@example.com' };
      const invalidData = { name: '', email: 'john@example.com' };
      
      expect(validateForm(validData, rules).isValid).toBe(true);
      expect(validateForm(invalidData, rules).isValid).toBe(false);
      expect(validateForm(invalidData, rules).errors.name).toBe('name is required');
    });

    test('should validate field lengths', () => {
      const rules = {
        username: { required: true, minLength: 3, maxLength: 20 },
        bio: { maxLength: 500 }
      };
      
      const validData = { username: 'john', bio: 'Short bio' };
      const invalidData = { username: 'jo', bio: 'a'.repeat(501) };
      
      expect(validateForm(validData, rules).isValid).toBe(true);
      expect(validateForm(invalidData, rules).isValid).toBe(false);
    });

    test('should validate patterns', () => {
      const rules = {
        phone: {
          pattern: /^\+?[\d\s\-\(\)]{10,}$/,
          patternError: 'Please enter a valid phone number'
        }
      };
      
      const validData = { phone: '+1 (555) 123-4567' };
      const invalidData = { phone: '123' };
      
      expect(validateForm(validData, rules).isValid).toBe(true);
      expect(validateForm(invalidData, rules).isValid).toBe(false);
      expect(validateForm(invalidData, rules).errors.phone).toBe('Please enter a valid phone number');
    });

    test('should handle custom validation', () => {
      const rules = {
        age: {
          required: true,
          custom: (value: number) => {
            if (value < 18) {
              return { isValid: false, error: 'Must be at least 18 years old' };
            }
            if (value > 120) {
              return { isValid: false, error: 'Age seems unrealistic' };
            }
            return { isValid: true };
          }
        }
      };
      
      expect(validateForm({ age: 25 }, rules).isValid).toBe(true);
      expect(validateForm({ age: 16 }, rules).isValid).toBe(false);
      expect(validateForm({ age: 150 }, rules).isValid).toBe(false);
    });
  });

  describe('Real-time Validation State Management', () => {
    interface ValidationState {
      errors: { [key: string]: string };
      touched: { [key: string]: boolean };
      isValidating: { [key: string]: boolean };
      isValid: boolean;
    }

    class RealTimeValidator {
      private state: ValidationState = {
        errors: {},
        touched: {},
        isValidating: {},
        isValid: true
      };

      private listeners: Array<(state: ValidationState) => void> = [];

      private updateState(updates: Partial<ValidationState>) {
        this.state = { ...this.state, ...updates };
        this.notifyListeners();
      }

      private notifyListeners() {
        this.listeners.forEach(listener => listener({ ...this.state }));
      }

      subscribe(listener: (state: ValidationState) => void) {
        this.listeners.push(listener);
        return () => {
          this.listeners = this.listeners.filter(l => l !== listener);
        };
      }

      validateField(fieldName: string, value: any, rules: any): Promise<{ isValid: boolean; error?: string }> {
        return new Promise((resolve) => {
          // Mark as validating
          this.updateState({
            isValidating: { ...this.state.isValidating, [fieldName]: true },
            touched: { ...this.state.touched, [fieldName]: true }
          });

          // Simulate async validation (e.g., API call)
          setTimeout(() => {
            const result = this.validateFieldSync(fieldName, value, rules);
            
            const newErrors = { ...this.state.errors };
            if (result.isValid) {
              delete newErrors[fieldName];
            } else {
              newErrors[fieldName] = result.error!;
            }

            this.updateState({
              errors: newErrors,
              isValidating: { ...this.state.isValidating, [fieldName]: false },
              isValid: Object.keys(newErrors).length === 0
            });

            resolve(result);
          }, 10); // Simulate small delay
        });
      }

      private validateFieldSync(fieldName: string, value: any, rules: any): { isValid: boolean; error?: string } {
        const fieldRules = rules[fieldName];
        if (!fieldRules) return { isValid: true };
        
        if (fieldRules.required && (!value || (typeof value === 'string' && value.trim() === ''))) {
          return { isValid: false, error: `${fieldName} is required` };
        }

        if (fieldRules.minLength && value && value.length < fieldRules.minLength) {
          return { isValid: false, error: `${fieldName} must be at least ${fieldRules.minLength} characters` };
        }

        return { isValid: true };
      }

      getState(): ValidationState {
        return { ...this.state };
      }

      reset() {
        this.state = {
          errors: {},
          touched: {},
          isValidating: {},
          isValid: true
        };
        this.notifyListeners();
      }

      setFieldTouched(fieldName: string, touched: boolean = true) {
        this.updateState({
          touched: { ...this.state.touched, [fieldName]: touched }
        });
      }

      clearError(fieldName: string) {
        const newErrors = { ...this.state.errors };
        delete newErrors[fieldName];
        this.updateState({
          errors: newErrors,
          isValid: Object.keys(newErrors).length === 0
        });
      }
    }

    test('should track field validation state correctly', async () => {
      const validator = new RealTimeValidator();
      const rules = { email: { required: true, minLength: 5 } };
      
      let stateUpdates: ValidationState[] = [];
      validator.subscribe(state => stateUpdates.push(state));
      
      // Initially no errors or touched fields
      expect(validator.getState().isValid).toBe(true);
      expect(validator.getState().touched.email).toBeFalsy();
      
      // Validate empty email
      await validator.validateField('email', '', rules);
      
      const state = validator.getState();
      expect(state.isValid).toBe(false);
      expect(state.touched.email).toBe(true);
      expect(state.errors.email).toBe('email is required');
      expect(stateUpdates.length).toBeGreaterThan(0);
    });

    test('should handle async validation flow', async () => {
      const validator = new RealTimeValidator();
      const rules = { username: { required: true, minLength: 3 } };
      
      let isValidatingStates: boolean[] = [];
      validator.subscribe(state => {
        if (state.isValidating.username !== undefined) {
          isValidatingStates.push(state.isValidating.username);
        }
      });
      
      // Start validation
      const validationPromise = validator.validateField('username', 'ab', rules);
      
      // Should be validating
      expect(validator.getState().isValidating.username).toBe(true);
      
      // Wait for validation to complete
      await validationPromise;
      
      // Should no longer be validating
      expect(validator.getState().isValidating.username).toBe(false);
      expect(validator.getState().errors.username).toBeDefined();
      
      // Should have tracked the validating state changes
      expect(isValidatingStates).toContain(true);
      expect(isValidatingStates).toContain(false);
    });

    test('should reset validation state', async () => {
      const validator = new RealTimeValidator();
      const rules = { name: { required: true } };
      
      // Add some errors and touched fields
      await validator.validateField('name', '', rules);
      validator.setFieldTouched('name', true);
      
      expect(validator.getState().isValid).toBe(false);
      expect(validator.getState().touched.name).toBe(true);
      expect(validator.getState().errors.name).toBeDefined();
      
      // Reset
      validator.reset();
      
      const state = validator.getState();
      expect(state.isValid).toBe(true);
      expect(state.touched.name).toBeFalsy();
      expect(state.errors.name).toBeUndefined();
    });

    test('should clear individual field errors', async () => {
      const validator = new RealTimeValidator();
      const rules = { 
        email: { required: true },
        name: { required: true }
      };
      
      // Add multiple errors
      await validator.validateField('email', '', rules);
      await validator.validateField('name', '', rules);
      
      expect(validator.getState().errors.email).toBeDefined();
      expect(validator.getState().errors.name).toBeDefined();
      expect(validator.getState().isValid).toBe(false);
      
      // Clear one error
      validator.clearError('email');
      
      const state = validator.getState();
      expect(state.errors.email).toBeUndefined();
      expect(state.errors.name).toBeDefined();
      expect(state.isValid).toBe(false); // Still invalid due to name error
    });

    test('should handle concurrent validations', async () => {
      const validator = new RealTimeValidator();
      const rules = { 
        field1: { required: true },
        field2: { required: true },
        field3: { minLength: 5 }
      };
      
      // Start multiple validations concurrently
      const promises = [
        validator.validateField('field1', 'value1', rules),
        validator.validateField('field2', '', rules), // Will fail
        validator.validateField('field3', 'test', rules) // Will fail
      ];
      
      await Promise.all(promises);
      
      const state = validator.getState();
      expect(state.touched.field1).toBe(true);
      expect(state.touched.field2).toBe(true);
      expect(state.touched.field3).toBe(true);
      
      expect(state.errors.field1).toBeUndefined(); // Valid
      expect(state.errors.field2).toBeDefined(); // Invalid - required
      expect(state.errors.field3).toBeDefined(); // Invalid - too short
      
      expect(state.isValid).toBe(false);
    });
  });
});
