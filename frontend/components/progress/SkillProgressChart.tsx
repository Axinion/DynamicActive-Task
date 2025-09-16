'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface SkillData {
  tag: string;
  mastery: number;
}

interface SkillProgressChartProps {
  data: SkillData[];
}

export function SkillProgressChart({ data }: SkillProgressChartProps) {
  // Transform data for the chart
  const chartData = data.map(item => ({
    tag: item.tag.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    mastery: Math.round(item.mastery * 100), // Convert to percentage
    rawMastery: item.mastery
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border rounded-lg shadow-lg">
          <p className="font-semibold">{label}</p>
          <p className="text-blue-600">
            Mastery: {data.mastery}%
          </p>
          <p className="text-sm text-gray-600">
            Raw Score: {data.rawMastery.toFixed(2)}
          </p>
        </div>
      );
    }
    return null;
  };

  if (data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-gray-500">
        <div className="text-center">
          <div className="text-sm mb-2">📊</div>
          <p>No skill data available yet</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          margin={{
            top: 20,
            right: 30,
            left: 20,
            bottom: 60,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis 
            dataKey="tag" 
            angle={-45}
            textAnchor="end"
            height={80}
            fontSize={12}
            stroke="#666"
          />
          <YAxis 
            domain={[0, 100]}
            tickFormatter={(value) => `${value}%`}
            fontSize={12}
            stroke="#666"
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar 
            dataKey="mastery" 
            fill="#3b82f6"
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
