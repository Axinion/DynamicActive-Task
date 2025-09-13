'use client';

import { useState } from 'react';
import { QuestionCreate } from '@/lib/api/assignments';

interface QuestionBuilderProps {
  questions: QuestionCreate[];
  onChange: (questions: QuestionCreate[]) => void;
}

export default function QuestionBuilder({ questions, onChange }: QuestionBuilderProps) {
  const [expandedQuestion, setExpandedQuestion] = useState<number | null>(null);

  const addQuestion = (type: 'mcq' | 'short') => {
    const newQuestion: QuestionCreate = {
      type,
      prompt: '',
      ...(type === 'mcq' ? { options: ['', ''], answer_key: '' } : { skill_tags: [] })
    };
    onChange([...questions, newQuestion]);
    setExpandedQuestion(questions.length);
  };

  const removeQuestion = (index: number) => {
    const newQuestions = questions.filter((_, i) => i !== index);
    onChange(newQuestions);
    if (expandedQuestion === index) {
      setExpandedQuestion(null);
    } else if (expandedQuestion !== null && expandedQuestion > index) {
      setExpandedQuestion(expandedQuestion - 1);
    }
  };

  const updateQuestion = (index: number, updates: Partial<QuestionCreate>) => {
    const newQuestions = [...questions];
    newQuestions[index] = { ...newQuestions[index], ...updates };
    onChange(newQuestions);
  };

  const addOption = (questionIndex: number) => {
    const question = questions[questionIndex];
    if (question.type === 'mcq' && question.options) {
      const newOptions = [...question.options, ''];
      updateQuestion(questionIndex, { options: newOptions });
    }
  };

  const removeOption = (questionIndex: number, optionIndex: number) => {
    const question = questions[questionIndex];
    if (question.type === 'mcq' && question.options && question.options.length > 2) {
      const newOptions = question.options.filter((_, i) => i !== optionIndex);
      const newAnswerKey = question.answer_key === question.options[optionIndex] ? '' : question.answer_key;
      updateQuestion(questionIndex, { options: newOptions, answer_key: newAnswerKey });
    }
  };

  const updateOption = (questionIndex: number, optionIndex: number, value: string) => {
    const question = questions[questionIndex];
    if (question.type === 'mcq' && question.options) {
      const newOptions = [...question.options];
      newOptions[optionIndex] = value;
      updateQuestion(questionIndex, { options: newOptions });
    }
  };

  const updateSkillTags = (questionIndex: number, tagsString: string) => {
    const tags = tagsString.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0);
    updateQuestion(questionIndex, { skill_tags: tags });
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Questions</h3>
        <div className="flex space-x-2">
          <button
            onClick={() => addQuestion('mcq')}
            className="px-3 py-1 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            + MCQ
          </button>
          <button
            onClick={() => addQuestion('short')}
            className="px-3 py-1 text-sm bg-green-600 text-white rounded-md hover:bg-green-700"
          >
            + Short Answer
          </button>
        </div>
      </div>

      {questions.length === 0 ? (
        <div className="text-center py-8 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No questions yet</h3>
          <p className="mt-1 text-sm text-gray-500">Add your first question to get started.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {questions.map((question, index) => (
            <div key={index} className="bg-white border border-gray-200 rounded-lg">
              <div className="p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-gray-500">Q{index + 1}</span>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      question.type === 'mcq' 
                        ? 'bg-blue-100 text-blue-800' 
                        : 'bg-green-100 text-green-800'
                    }`}>
                      {question.type === 'mcq' ? 'MCQ' : 'Short Answer'}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => setExpandedQuestion(expandedQuestion === index ? null : index)}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      <svg 
                        className={`w-5 h-5 transform transition-transform ${
                          expandedQuestion === index ? 'rotate-180' : ''
                        }`} 
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                    <button
                      onClick={() => removeQuestion(index)}
                      className="text-red-400 hover:text-red-600"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>

                {/* Question Preview */}
                <div className="mb-3">
                  <p className="text-sm text-gray-700">
                    {question.prompt || 'Enter question prompt...'}
                  </p>
                  {question.type === 'mcq' && question.options && (
                    <div className="mt-2 space-y-1">
                      {question.options.map((option, optionIndex) => (
                        <div key={optionIndex} className="flex items-center space-x-2">
                          <span className="text-xs text-gray-500 w-4">
                            {String.fromCharCode(65 + optionIndex)}.
                          </span>
                          <span className="text-xs text-gray-600">
                            {option || 'Option ' + (optionIndex + 1)}
                          </span>
                          {question.answer_key === option && (
                            <span className="text-xs text-green-600 font-medium">✓ Correct</span>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Expanded Form */}
                {expandedQuestion === index && (
                  <div className="space-y-4 pt-3 border-t border-gray-200">
                    {/* Question Prompt */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Question Prompt *
                      </label>
                      <textarea
                        value={question.prompt}
                        onChange={(e) => updateQuestion(index, { prompt: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        rows={3}
                        placeholder="Enter your question..."
                      />
                    </div>

                    {/* MCQ Options */}
                    {question.type === 'mcq' && (
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <label className="block text-sm font-medium text-gray-700">
                            Answer Options *
                          </label>
                          <button
                            onClick={() => addOption(index)}
                            className="text-sm text-blue-600 hover:text-blue-800"
                          >
                            + Add Option
                          </button>
                        </div>
                        <div className="space-y-2">
                          {question.options?.map((option, optionIndex) => (
                            <div key={optionIndex} className="flex items-center space-x-2">
                              <span className="text-sm text-gray-500 w-6">
                                {String.fromCharCode(65 + optionIndex)}.
                              </span>
                              <input
                                type="text"
                                value={option}
                                onChange={(e) => updateOption(index, optionIndex, e.target.value)}
                                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                placeholder={`Option ${optionIndex + 1}`}
                              />
                              <button
                                onClick={() => removeOption(index, optionIndex)}
                                disabled={question.options && question.options.length <= 2}
                                className="text-red-400 hover:text-red-600 disabled:opacity-50 disabled:cursor-not-allowed"
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                              </button>
                            </div>
                          ))}
                        </div>

                        {/* Correct Answer Selection */}
                        <div className="mt-3">
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Correct Answer *
                          </label>
                          <select
                            value={question.answer_key || ''}
                            onChange={(e) => updateQuestion(index, { answer_key: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          >
                            <option value="">Select correct answer...</option>
                            {question.options?.map((option, optionIndex) => (
                              <option key={optionIndex} value={option}>
                                {String.fromCharCode(65 + optionIndex)}. {option}
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>
                    )}

                    {/* Skill Tags */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Skill Tags
                      </label>
                      <input
                        type="text"
                        value={question.skill_tags?.join(', ') || ''}
                        onChange={(e) => updateSkillTags(index, e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Enter skill tags separated by commas (e.g., algebra, problem-solving)"
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        Separate multiple tags with commas
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
