import mongoose, { Schema, Document } from 'mongoose';
import bcrypt from 'bcryptjs';

export interface IUser extends Document {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  profile: {
    avatar?: string;
    cvUrl?: string;
    linkedinUrl?: string;
    skills: string[];
    experience: {
      title: string;
      company: string;
      startDate: Date;
      endDate?: Date;
      description: string;
    }[];
    education: {
      school: string;
      degree: string;
      field: string;
      startDate: Date;
      endDate?: Date;
    }[];
  };
  preferences: {
    jobTypes: string[];
    locations: string[];
    skills: string[];
    salary: {
      min?: number;
      currency: string;
    };
  };
  savedJobs: mongoose.Types.ObjectId[];
  applications: {
    jobId: mongoose.Types.ObjectId;
    status: string;
    appliedAt: Date;
    updatedAt: Date;
  }[];
  lastLogin: Date;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
  comparePassword(candidatePassword: string): Promise<boolean>;
}

const UserSchema: Schema = new Schema({
  email: { 
    type: String, 
    required: true, 
    unique: true,
    trim: true,
    lowercase: true
  },
  password: { 
    type: String, 
    required: true 
  },
  firstName: { 
    type: String, 
    required: true 
  },
  lastName: { 
    type: String, 
    required: true 
  },
  profile: {
    avatar: String,
    cvUrl: String,
    linkedinUrl: String,
    skills: [String],
    experience: [{
      title: String,
      company: String,
      startDate: Date,
      endDate: Date,
      description: String
    }],
    education: [{
      school: String,
      degree: String,
      field: String,
      startDate: Date,
      endDate: Date
    }]
  },
  preferences: {
    jobTypes: [String],
    locations: [String],
    skills: [String],
    salary: {
      min: Number,
      currency: { type: String, default: 'USD' }
    }
  },
  savedJobs: [{ type: Schema.Types.ObjectId, ref: 'Job' }],
  applications: [{
    jobId: { type: Schema.Types.ObjectId, ref: 'Job' },
    status: { 
      type: String, 
      enum: ['applied', 'interviewing', 'offered', 'rejected', 'withdrawn'],
      default: 'applied'
    },
    appliedAt: { type: Date, default: Date.now },
    updatedAt: { type: Date, default: Date.now }
  }],
  lastLogin: { type: Date },
  isActive: { type: Boolean, default: true }
}, {
  timestamps: true
});

// Hash password before saving
UserSchema.pre('save', async function(next) {
  if (!this.isModified('password')) return next();
  
  try {
    const salt = await bcrypt.genSalt(10);
    this.password = await bcrypt.hash(this.password, salt);
    next();
  } catch (error: any) {
    next(error);
  }
});

// Compare password method
UserSchema.methods.comparePassword = async function(candidatePassword: string): Promise<boolean> {
  return bcrypt.compare(candidatePassword, this.password);
};

// Indexes
UserSchema.index({ email: 1 });
UserSchema.index({ 'profile.skills': 1 });
UserSchema.index({ 'preferences.jobTypes': 1, 'preferences.locations': 1 });

export default mongoose.model<IUser>('User', UserSchema); 