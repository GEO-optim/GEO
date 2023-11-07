# metrics = ['relevance_detailed', 'uniqueness_detailed', 'subjcount_detailed', 'follow_detailed', 'simple_wordpos', 'simple_pos', 'influence_detailed', 'subjective_score', 'diversity_detailed', 'simple_word', 'subjpos_detailed']
columns = ['Method', 'Word', 'Position', 'WordPos Overall', 'Rel.', 'Infl.', 'Unique', 'Div.', 'FollowUp', 'Pos.', 'Count', 'Subjective Average', 'source']
metric_dict = {
    'Word': 'simple_word',
    'Position': 'simple_pos',
    'WordPos Overall': 'simple_wordpos',
    'Rel.': 'relevance_detailed',
    'Infl.': 'influence_detailed',
    'Unique': 'uniqueness_detailed',
    'Div.': 'diversity_detailed',
    'FollowUp': 'follow_detailed',  
    'Pos.': 'subjpos_detailed',
    'Count': 'subjcount_detailed',
    'Subjective Average': 'subjective_score',
}

tags = {
    "Difficulty Level": ["Simple", "Intermediate", "Complex", "Multi-faceted", "Open-ended", 'any'],
    "Nature of Query": ["Informational", "Navigational", "Transactional", "Debate", "Opinion", "Comparison", "Instructional", "Descriptive", "Predictive", 'any'],
    "Sensitivity": ["Sensitive", "Non-sensitive",'any'],
    "Genre": [
        "🎭 Arts and Entertainment", "🚗 Autos and Vehicles", "💄 Beauty and Fitness", "📚 Books and Literature", "🏢 Business and Industrial",
        "💻 Computers and Electronics", "💰 Finance", "🍔 Food and Drink", "🎮 Games", "🏥 Health", "🎨 Hobbies and Leisure", "🏡 Home and Garden",
        "🌐 Internet and Telecom", "🎓 Jobs and Education", "🏛️ Law and Government", "📰 News", "💬 Online Communities", "👫 People and Society",
        "🐾 Pets and Animals", "🏡 Real Estate", "📚 Reference", "🔬 Science", "🛒 Shopping", "⚽ Sports", "✈️ Travel",'any'
    ],
    "Specific Topics": ["Physics", "Chemistry", "Biology", "Mathematics", "Computer Science", "Economics", 'any'],
    "User Intent": ["🔍 Research", "💰 Purchase", "🎉 Entertainment", "📚 Learning", "🔄 Comparison", 'any'],
    "Answer Type": ["Fact", "Opinion", "List", "Explanation", "Guide", "Comparison", "Prediction", 'any'],
}

