import mongoose, { Schema, Document } from 'mongoose';

export interface ICompany extends Document {
  name: string;
  website: string;
  logo: string;
  description: string;
  industry: string;
  size: string;
  location: string;
  remotePolicy: string;
  benefits: string[];
  techStack: string[];
  socialLinks: {
    linkedin?: string;
    twitter?: string;
    github?: string;
  };
  createdAt: Date;
  updatedAt: Date;
}

const CompanySchema: Schema = new Schema({
  name: { type: String, required: true },
  website: { type: String, required: true },
  logo: { type: String },
  description: { type: String },
  industry: { type: String },
  size: { type: String },
  location: { type: String },
  remotePolicy: { type: String },
  benefits: [{ type: String }],
  techStack: [{ type: String }],
  socialLinks: {
    linkedin: { type: String },
    twitter: { type: String },
    github: { type: String }
  }
}, {
  timestamps: true
});

export default mongoose.model<ICompany>('Company', CompanySchema); 