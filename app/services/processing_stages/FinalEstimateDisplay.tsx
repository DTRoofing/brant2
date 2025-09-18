'use client'

import React from 'react';
import { AreaChart, DollarSign, Clock, Check, List, Users } from 'lucide-react';

interface FinalEstimateResponse {
  total_area_sqft: number;
  estimated_cost: number;
  materials_needed: any[];
  labor_estimate: {
    estimated_hours: number;
    crew_size: number;
    total_labor_cost: number;
  };
  timeline_estimate: string;
  confidence_score: number;
  processing_metadata: any;
  document_info: {
    filename: string;
    upload_date: string;
  };
}

interface EstimateDisplayProps {
  estimateData: FinalEstimateResponse | null;
}

const StatCard: React.FC<{ icon: React.ReactNode; label: string; value: string | number; }> = ({ icon, label, value }) => (
  <div className="bg-gray-50 p-4 rounded-lg flex items-center shadow-sm">
    <div className="p-3 bg-blue-100 text-blue-600 rounded-full mr-4">
      {icon}
    </div>
    <div>
      <p className="text-sm font-medium text-gray-500">{label}</p>
      <p className="text-xl font-semibold text-gray-800">{value}</p>
    </div>
  </div>
);

export const FinalEstimateDisplay: React.FC<EstimateDisplayProps> = ({ estimateData }) => {
  if (!estimateData) {
    return null;
  }

  return (
    <div className="mt-8 bg-white rounded-lg shadow-lg p-8 animate-fade-in">
      <div className="flex justify-between items-start mb-6 border-b pb-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Generated Estimate</h2>
          <p className="text-sm text-gray-500">File: {estimateData.document_info.filename}</p>
        </div>
        <div className="text-right">
          <p className="text-sm font-medium text-gray-500">Confidence Score</p>
          <p className={`text-2xl font-bold ${
            estimateData.confidence_score > 0.8 ? 'text-green-600' :
            estimateData.confidence_score > 0.6 ? 'text-yellow-600' : 'text-red-600'
          }`}>
            {(estimateData.confidence_score * 100).toFixed(1)}%
          </p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <StatCard 
          icon={<AreaChart size={24} />} 
          label="Total Roof Area" 
          value={`${estimateData.total_area_sqft.toLocaleString()} sqft`} 
        />
        <StatCard 
          icon={<DollarSign size={24} />} 
          label="Estimated Cost" 
          value={`$${estimateData.estimated_cost.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`} 
        />
        <StatCard 
          icon={<Clock size={24} />} 
          label="Estimated Timeline" 
          value={estimateData.timeline_estimate} 
        />
        <StatCard 
          icon={<Users size={24} />} 
          label="Labor Cost" 
          value={`$${estimateData.labor_estimate.total_labor_cost.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`} 
        />
      </div>

      <div>
        <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center"><List size={20} className="mr-2" /> Materials Needed</h3>
        <div className="bg-gray-50 p-4 rounded-lg">
          <ul className="list-disc list-inside text-gray-700 space-y-1">
            {estimateData.materials_needed && estimateData.materials_needed.length > 0 ? (
              estimateData.materials_needed.map((material, index) => (
                <li key={index}>
                  {material.type || 'Unknown Material'}
                  {material.quantity && ` - ${material.quantity.toLocaleString()} sqft`}
                </li>
              ))
            ) : (
              <li>No specific materials identified.</li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
};