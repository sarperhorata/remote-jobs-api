import { StorageService } from './StorageService';

export class UserProfileService {
  static async uploadCV(userId: string, file: File): Promise<string> {
    try {
      const path = StorageService.getFilePath(userId, file.name);
      const downloadURL = await StorageService.uploadFile(file, path);
      
      // Update user profile with new CV URL
      await this.updateUserProfile(userId, { cvUrl: downloadURL });
      
      return downloadURL;
    } catch (error) {
      console.error('Error uploading CV:', error);
      throw new Error('Failed to upload CV');
    }
  }

  static async importLinkedInProfile(userId: string, linkedinUrl: string): Promise<void> {
    try {
      // TODO: Implement LinkedIn API integration
      // For now, just update the profile with the LinkedIn URL
      await this.updateUserProfile(userId, { linkedinUrl });
    } catch (error) {
      console.error('Error importing LinkedIn profile:', error);
      throw new Error('Failed to import LinkedIn profile');
    }
  }

  private static async updateUserProfile(userId: string, data: Partial<UserProfile>): Promise<void> {
    try {
      const response = await fetch(`/api/users/${userId}/profile`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error('Failed to update user profile');
      }
    } catch (error) {
      console.error('Error updating user profile:', error);
      throw error;
    }
  }
}

interface UserProfile {
  cvUrl?: string;
  linkedinUrl?: string;
  skills: string[];
  experience: Experience[];
  education: Education[];
}

interface Experience {
  title: string;
  company: string;
  startDate: string;
  endDate?: string;
  description: string;
}

interface Education {
  school: string;
  degree: string;
  field: string;
  startDate: string;
  endDate?: string;
} 