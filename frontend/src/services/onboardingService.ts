import { getApiUrl } from '../utils/apiConfig';

export interface OnboardingStep {
  message: string;
  user_id?: string;
  onboarding_step: number;
  next_step: string;
  access_token?: string;
}

export interface EmailOnlyRegister {
  email: string;
}

export interface EmailVerification {
  token: string;
}

export interface SetPassword {
  token: string;
  password: string;
  confirm_password: string;
}

export interface ProfileCompletion {
  name?: string;
  bio?: string;
  location?: string;
  skills?: string[];
  experience_years?: number;
  job_preferences?: Record<string, any>;
}

export interface OnboardingStatus {
  user_id: string;
  onboarding_step: number;
  next_step: string;
  email_verified: boolean;
  onboarding_completed: boolean;
  has_linkedin: boolean;
  has_resume: boolean;
}

class OnboardingService {
  private async getApiUrl(): Promise<string> {
    return await getApiUrl();
  }

  async registerWithEmail(email: string): Promise<OnboardingStep> {
    const apiUrl = await this.getApiUrl();
    const response = await fetch(`${apiUrl}/onboarding/register-email`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Email kayıt işlemi başarısız');
    }

    return response.json();
  }

  async verifyEmail(token: string): Promise<OnboardingStep> {
    const apiUrl = await this.getApiUrl();
    const response = await fetch(`${apiUrl}/onboarding/verify-email`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ token }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Email doğrulama başarısız');
    }

    return response.json();
  }

  async setPassword(token: string, password: string, confirmPassword: string): Promise<OnboardingStep> {
    const apiUrl = await this.getApiUrl();
    const response = await fetch(`${apiUrl}/onboarding/set-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        token, 
        password, 
        confirm_password: confirmPassword 
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Şifre belirleme başarısız');
    }

    return response.json();
  }

  async getLinkedInAuthUrl(): Promise<{ auth_url: string; state: string }> {
    const apiUrl = await this.getApiUrl();
    const response = await fetch(`${apiUrl}/onboarding/linkedin-auth-url`);

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'LinkedIn auth URL alınamadı');
    }

    return response.json();
  }

  async handleLinkedInCallback(code: string, state: string, userId: string): Promise<OnboardingStep> {
    const apiUrl = await this.getApiUrl();
    const response = await fetch(`${apiUrl}/onboarding/linkedin-callback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code, state, user_id: userId }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'LinkedIn bağlantısı başarısız');
    }

    return response.json();
  }

  async uploadCV(userId: string, file: File): Promise<{ message: string; file_url: string }> {
    const apiUrl = await this.getApiUrl();
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);

    const response = await fetch(`${apiUrl}/onboarding/upload-cv`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'CV yükleme başarısız');
    }

    return response.json();
  }

  async completeProfile(userId: string, profileData: ProfileCompletion): Promise<OnboardingStep> {
    const apiUrl = await this.getApiUrl();
    const response = await fetch(`${apiUrl}/onboarding/complete-profile?user_id=${userId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(profileData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Profil tamamlama başarısız');
    }

    return response.json();
  }

  async getOnboardingStatus(userId: string): Promise<OnboardingStatus> {
    const apiUrl = await this.getApiUrl();
    const response = await fetch(`${apiUrl}/onboarding/status/${userId}`);

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Onboarding durumu alınamadı');
    }

    return response.json();
  }

  // URL'den token parametresini al
  getTokenFromUrl(): string | null {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('token');
  }

  // URL'den LinkedIn callback parametrelerini al
  getLinkedInCallbackParams(): { code: string | null; state: string | null } {
    const urlParams = new URLSearchParams(window.location.search);
    return {
      code: urlParams.get('code'),
      state: urlParams.get('state'),
    };
  }
}

export const onboardingService = new OnboardingService(); 