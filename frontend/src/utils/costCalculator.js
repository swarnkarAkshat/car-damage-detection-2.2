export const getDamageDetails = (prediction) => {
  if (!prediction) return { damage: 0, cost: 0 };
  
  const formatted = prediction.toLowerCase();
  
  if (formatted.includes('normal')) {
    return { damage: 0, cost: 0 };
  } else if (formatted.includes('breakage')) {
    return { damage: 40, cost: 6000 };
  } else if (formatted.includes('crushed')) {
    return { damage: 60, cost: 9000 };
  }
  
  return { damage: 0, cost: 0 };
};

export const cleanAIExplanation = (rawText) => {
  if (!rawText) return '';
  // Match the inner JSON string if it's wrapped in markdown json block
  try {
    let cleanText = rawText.replace(/```json/g, '').replace(/```/g, '').trim();
    if (cleanText.startsWith('{') || cleanText.startsWith('[')) {
       const parsed = JSON.parse(cleanText);
       // Check if there is a flat explanation or multiple keys
       return parsed.explanation || parsed.recommendations 
          ? `${parsed.explanation || ''}\n\n${parsed.recommendations || ''}`.trim()
          : JSON.stringify(parsed, null, 2);
    }
  } catch(e) {
    // If it's not strictly parseable json, just return without markers
  }
  return rawText.replace(/```json/g, '').replace(/```/g, '').trim();
};
