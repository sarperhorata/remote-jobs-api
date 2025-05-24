import mongoose, { Schema, Document } from 'mongoose';

export interface IJob extends Document {
  title: string;
  companyId: mongoose.Types.ObjectId;
  description: string;
  requirements: string[];
  responsibilities: string[];
  skills: string[];
  location: string;
  type: string;
  salary: {
    min?: number;
    max?: number;
    currency: string;
  };
  experience: {
    min?: number;
    max?: number;
  };
  education: string;
  benefits: string[];
  applicationUrl: string;
  source: string;
  sourceUrl: string;
  status: string;
  postedAt: Date;
  expiresAt?: Date;
  createdAt: Date;
  updatedAt: Date;
}

const JobSchema: Schema = new Schema({
  title: { type: String, required: true },
  companyId: { type: Schema.Types.ObjectId, ref: 'Company', required: true },
  description: { type: String, required: true },
  requirements: [{ type: String }],
  responsibilities: [{ type: String }],
  skills: [{ type: String }],
  location: { type: String, required: true },
  type: { type: String, required: true },
  salary: {
    min: { type: Number },
    max: { type: Number },
    currency: { type: String, default: 'USD' }
  },
  experience: {
    min: { type: Number },
    max: { type: Number }
  },
  education: { type: String },
  benefits: [{ type: String }],
  applicationUrl: { type: String, required: true },
  source: { type: String, required: true },
  sourceUrl: { type: String, required: true },
  status: { 
    type: String, 
    enum: ['active', 'expired', 'closed'],
    default: 'active'
  },
  postedAt: { type: Date, required: true },
  expiresAt: { type: Date }
}, {
  timestamps: true
});

// Indexes for better search performance
JobSchema.index({ title: 'text', description: 'text', skills: 'text' });
JobSchema.index({ companyId: 1, status: 1 });
JobSchema.index({ location: 1, type: 1, status: 1 });
JobSchema.index({ postedAt: -1 });

export default mongoose.model<IJob>('Job', JobSchema); 