import React, { useState, useEffect } from 'react';
import { Tag, Plus, X, Edit3, Save, CheckCircle, AlertCircle, Loader, FileText } from 'lucide-react';
import { toast } from 'react-hot-toast';

interface Skill {
  id: string;
  name: string;
  category?: string;
  confidence?: number;
  source: 'cv' | 'manual' | 'ai';
}

interface SkillsExtractionProps {
  skills: Skill[];
  onSkillsUpdate: (skills: Skill[]) => void;
  isExtracting?: boolean;
  className?: string;
}

const SkillsExtraction: React.FC<SkillsExtractionProps> = ({
  skills,
  onSkillsUpdate,
  isExtracting = false,
  className = ''
}) => {
  const [editingSkills, setEditingSkills] = useState<Skill[]>(skills);
  const [isEditing, setIsEditing] = useState(false);
  const [newSkill, setNewSkill] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('technical');

  const categories = [
    { id: 'technical', name: 'Technical Skills', color: 'bg-blue-100 text-blue-800' },
    { id: 'soft', name: 'Soft Skills', color: 'bg-green-100 text-green-800' },
    { id: 'languages', name: 'Languages', color: 'bg-purple-100 text-purple-800' },
    { id: 'tools', name: 'Tools & Platforms', color: 'bg-orange-100 text-orange-800' },
    { id: 'certifications', name: 'Certifications', color: 'bg-red-100 text-red-800' }
  ];

  useEffect(() => {
    setEditingSkills(skills);
  }, [skills]);

  const addSkill = () => {
    if (!newSkill.trim()) return;

    const skillExists = editingSkills.some(skill => 
      skill.name.toLowerCase() === newSkill.trim().toLowerCase()
    );

    if (skillExists) {
      toast.error('This skill already exists');
      return;
    }

    const newSkillObj: Skill = {
      id: Date.now().toString(),
      name: newSkill.trim(),
      category: selectedCategory,
      source: 'manual',
      confidence: 100
    };

    setEditingSkills([...editingSkills, newSkillObj]);
    setNewSkill('');
    toast.success('Skill added successfully');
  };

  const removeSkill = (skillId: string) => {
    setEditingSkills(editingSkills.filter(skill => skill.id !== skillId));
  };

  const updateSkill = (skillId: string, updates: Partial<Skill>) => {
    setEditingSkills(editingSkills.map(skill => 
      skill.id === skillId ? { ...skill, ...updates } : skill
    ));
  };

  const saveChanges = () => {
    onSkillsUpdate(editingSkills);
    setIsEditing(false);
    toast.success('Skills updated successfully');
  };

  const cancelEditing = () => {
    setEditingSkills(skills);
    setIsEditing(false);
  };

  const getSkillSourceIcon = (source: string) => {
    switch (source) {
      case 'cv':
        return <FileText size={12} className="text-blue-600" />;
      case 'ai':
        return <CheckCircle size={12} className="text-green-600" />;
      case 'manual':
        return <Edit3 size={12} className="text-gray-600" />;
      default:
        return null;
    }
  };

  const getSkillSourceTooltip = (source: string) => {
    switch (source) {
      case 'cv':
        return 'Extracted from CV';
      case 'ai':
        return 'AI enhanced';
      case 'manual':
        return 'Manually added';
      default:
        return '';
    }
  };

  const groupedSkills = editingSkills.reduce((acc, skill) => {
    const category = skill.category || 'technical';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(skill);
    return acc;
  }, {} as Record<string, Skill[]>);

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Skills & Expertise</h3>
          <p className="text-sm text-gray-600">
            {isExtracting ? 'Extracting skills from your CV...' : `${editingSkills.length} skills found`}
          </p>
        </div>
        
        {!isExtracting && (
          <div className="flex items-center space-x-2">
            {isEditing ? (
              <>
                <button
                  onClick={saveChanges}
                  className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 transition-colors"
                >
                  <Save size={14} className="mr-1" />
                  Save
                </button>
                <button
                  onClick={cancelEditing}
                  className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Cancel
                </button>
              </>
            ) : (
              <button
                onClick={() => setIsEditing(true)}
                className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
              >
                <Edit3 size={14} className="mr-1" />
                Edit Skills
              </button>
            )}
          </div>
        )}
      </div>

      {/* Loading State */}
      {isExtracting && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
          <Loader className="animate-spin mx-auto mb-3" size={24} />
          <p className="text-blue-800 font-medium">Analyzing your CV...</p>
          <p className="text-sm text-blue-600 mt-1">Extracting skills and expertise</p>
        </div>
      )}

      {/* Add New Skill */}
      {isEditing && (
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-3">Add New Skill</h4>
          <div className="flex gap-3">
            <input
              type="text"
              value={newSkill}
              onChange={(e) => setNewSkill(e.target.value)}
              placeholder="Enter skill name..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              onKeyDown={(e) => e.key === 'Enter' && addSkill()}
            />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {categories.map(category => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
            <button
              onClick={addSkill}
              data-testid="add-skill-button"
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus size={16} />
            </button>
          </div>
        </div>
      )}

      {/* Skills Display */}
      {!isExtracting && editingSkills.length > 0 && (
        <div className="space-y-4">
          {categories.map(category => {
            const categorySkills = groupedSkills[category.id] || [];
            if (categorySkills.length === 0) return null;

            return (
              <div key={category.id} className="space-y-3">
                <h4 className="font-medium text-gray-900 flex items-center">
                  <span className={`inline-block w-3 h-3 rounded-full mr-2 ${category.color.replace('bg-', '').replace(' text-', ' bg-')}`}></span>
                  {category.name}
                  <span className="ml-2 text-sm text-gray-500">({categorySkills.length})</span>
                </h4>
                
                <div className="flex flex-wrap gap-2">
                  {categorySkills.map(skill => (
                    <div
                      key={skill.id}
                      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                        isEditing 
                          ? 'bg-gray-100 text-gray-800 hover:bg-gray-200' 
                          : category.color
                      }`}
                      title={getSkillSourceTooltip(skill.source)}
                    >
                      {getSkillSourceIcon(skill.source)}
                      <span>{skill.name}</span>
                      
                      {skill.confidence && skill.confidence < 100 && (
                        <span className="text-xs opacity-75">
                          ({skill.confidence}%)
                        </span>
                      )}
                      
                      {isEditing && (
                        <button
                          onClick={() => removeSkill(skill.id)}
                          className="ml-1 hover:text-red-600 transition-colors"
                        >
                          <X size={12} />
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Empty State */}
      {!isExtracting && editingSkills.length === 0 && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
          <Tag className="mx-auto mb-3 text-gray-400" size={32} />
          <h4 className="font-medium text-gray-900 mb-2">No Skills Found</h4>
          <p className="text-gray-600 mb-4">
            Upload your CV to automatically extract skills, or add them manually.
          </p>
          {!isEditing && (
            <button
              onClick={() => setIsEditing(true)}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus size={16} className="mr-2" />
              Add Skills Manually
            </button>
          )}
        </div>
      )}

      {/* Skills Summary */}
      {!isExtracting && editingSkills.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4 text-sm">
              <div className="flex items-center space-x-1">
                <FileText size={14} className="text-blue-600" />
                <span className="text-blue-800">
                  {editingSkills.filter(s => s.source === 'cv').length} from CV
                </span>
              </div>
              <div className="flex items-center space-x-1">
                <CheckCircle size={14} className="text-green-600" />
                <span className="text-green-800">
                  {editingSkills.filter(s => s.source === 'ai').length} AI enhanced
                </span>
              </div>
              <div className="flex items-center space-x-1">
                <Edit3 size={14} className="text-gray-600" />
                <span className="text-gray-700">
                  {editingSkills.filter(s => s.source === 'manual').length} manual
                </span>
              </div>
            </div>
            
            {editingSkills.some(s => s.confidence && s.confidence < 100) && (
              <div className="flex items-center space-x-1 text-amber-700">
                <AlertCircle size={14} />
                <span className="text-sm">
                  Some skills have low confidence scores
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default SkillsExtraction; 