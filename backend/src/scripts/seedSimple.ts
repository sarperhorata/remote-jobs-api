import mongoose from 'mongoose';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const mongoUri = 'mongodb+srv://myremotejobs:cH622T5iGoc9tzfe@remotejobs.tn0gxu0.mongodb.net/remotejobs?retryWrites=true&w=majority&appName=RemoteJobs';

async function seedSimple() {
  try {
    console.log(`Attempting to connect to MongoDB with URI: ${mongoUri}`);
    
    // Connect to MongoDB with detailed options
    await mongoose.connect(mongoUri, {
      connectTimeoutMS: 10000, // 10 seconds
      socketTimeoutMS: 45000,  // 45 seconds
    });
    
    console.log('Successfully connected to MongoDB!');
    
    // Get database information
    const db = mongoose.connection.db;
    const collections = await db.listCollections().toArray();
    console.log('Available collections:');
    collections.forEach(collection => {
      console.log(`- ${collection.name}`);
    });
    
    // Close connection
    await mongoose.connection.close();
    console.log('MongoDB connection closed');
    
  } catch (error) {
    console.error('Error connecting to MongoDB:', error);
    process.exit(1);
  }
}

// Run the seed function
seedSimple(); 