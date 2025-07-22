import { User } from '../contexts/AuthContext';

export interface SubscriptionPlan {
  type: 'free' | 'pro' | 'premium' | 'enterprise';
  name: string;
  features: string[];
  isActive: boolean;
  expiresAt?: Date;
}

export const isPremiumUser = (user: User | null): boolean => {
  if (!user) return false;
  
  // Check subscription status
  if (user.subscription_type === 'premium' || user.subscription_type === 'enterprise') {
    return true;
  }
  
  // Check subscription plan
  if (user.subscription_type === 'premium' || user.subscription_type === 'enterprise') {
    return true;
  }
  
  // Check if user has active subscription
  if (user.subscription_status === 'active' && user.subscription_end_date) {
    const endDate = new Date(user.subscription_end_date);
    return endDate > new Date();
  }
  
  return false;
};

export const getUserSubscriptionPlan = (user: User | null): SubscriptionPlan => {
  if (!user) {
    return {
      type: 'free',
      name: 'Free Plan',
      features: [
        'Basic job search',
        'Limited job views',
        'Basic profile',
        'Email notifications'
      ],
      isActive: false
    };
  }

  const subscriptionType = user.subscription_type || 'free';
  
  switch (subscriptionType) {
    case 'premium':
    case 'enterprise':
      return {
        type: subscriptionType as 'premium' | 'enterprise',
        name: subscriptionType === 'premium' ? 'Premium Plan' : 'Enterprise Plan',
        features: [
          'Unlimited job access',
          'AI-powered job matching',
          'AI CV analysis',
          'Priority support',
          'Advanced filters',
          'Salary insights',
          'Auto-apply feature',
          'Resume optimization'
        ],
        isActive: true,
        expiresAt: user.subscription_end_date ? new Date(user.subscription_end_date) : undefined
      };
    
    case 'pro':
      return {
        type: 'pro',
        name: 'Pro Plan',
        features: [
          'Enhanced job search',
          'More job views',
          'Advanced filters',
          'Resume builder',
          'Email support'
        ],
        isActive: true,
        expiresAt: user.subscription_end_date ? new Date(user.subscription_end_date) : undefined
      };
    
    default:
      return {
        type: 'free',
        name: 'Free Plan',
        features: [
          'Basic job search',
          'Limited job views',
          'Basic profile',
          'Email notifications'
        ],
        isActive: false
      };
  }
};

export const getPremiumFeatureMessage = (featureName: string): string => {
  return `🔒 ${featureName} is a premium feature. Upgrade to Premium to unlock this and many more advanced features!`;
};

export const getUpgradeButtonText = (currentPlan: SubscriptionPlan): string => {
  switch (currentPlan.type) {
    case 'free':
      return 'Upgrade to Premium';
    case 'pro':
      return 'Upgrade to Premium';
    case 'premium':
      return 'Manage Subscription';
    case 'enterprise':
      return 'Contact Support';
    default:
      return 'Upgrade to Premium';
  }
};

export const getUpgradeUrl = (currentPlan: SubscriptionPlan): string => {
  switch (currentPlan.type) {
    case 'free':
    case 'pro':
      return '/pricing';
    case 'premium':
      return '/account/subscription';
    case 'enterprise':
      return '/contact';
    default:
      return '/pricing';
  }
}; 