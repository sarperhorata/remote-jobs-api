describe('Data Validation Tests', () => {
  describe('Form Validation', () => {
    describe('Email Validation', () => {
      const validateEmail = (email: string): boolean => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
      };

      it('should validate correct email formats', () => {
        const validEmails = [
          'test@example.com',
          'user.name@domain.co.uk',
          'admin+tag@site.org'
        ];

        validEmails.forEach(email => {
          expect(validateEmail(email)).toBe(true);
        });
      });

      it('should reject invalid email formats', () => {
        const invalidEmails = [
          'invalid-email',
          '@domain.com',
          'user@',
          ''
        ];

        invalidEmails.forEach(email => {
          expect(validateEmail(email)).toBe(false);
        });
      });
    });

    describe('Password Validation', () => {
      const validatePassword = (password: string): boolean => {
        const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$/;
        return passwordRegex.test(password);
      };

      it('should validate strong passwords', () => {
        const strongPasswords = [
          'Password123',
          'MyPass123!',
          'SecureP@ss1'
        ];

        strongPasswords.forEach(password => {
          expect(validatePassword(password)).toBe(true);
        });
      });

      it('should reject weak passwords', () => {
        const weakPasswords = [
          '123',
          'password',
          'pass123'
        ];

        weakPasswords.forEach(password => {
          expect(validatePassword(password)).toBe(false);
        });
      });
    });
  });

  describe('Data Sanitization', () => {
    const sanitizeString = (input: string): string => {
      return input.trim().replace(/[<>\"']/g, '');
    };

    it('should remove dangerous characters', () => {
      const input = '<script>alert("xss")</script>';
      const result = sanitizeString(input);
      
      expect(result).not.toContain('<');
      expect(result).not.toContain('>');
    });

    it('should trim whitespace', () => {
      const input = '  test string  ';
      const result = sanitizeString(input);
      
      expect(result).toBe('test string');
    });
  });

  describe('Number Validation', () => {
    const validatePositiveNumber = (value: any): boolean => {
      const num = Number(value);
      return !isNaN(num) && num > 0;
    };

    it('should validate positive numbers', () => {
      const validNumbers = [1, 100, 1.5, '42'];
      
      validNumbers.forEach(num => {
        expect(validatePositiveNumber(num)).toBe(true);
      });
    });

    it('should reject invalid numbers', () => {
      const invalidNumbers = [0, -1, 'abc', null];
      
      invalidNumbers.forEach(num => {
        expect(validatePositiveNumber(num)).toBe(false);
      });
    });
  });
});
