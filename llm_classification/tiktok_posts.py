# Cell 1
import pandas as pd
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define categories
categorias = [
    "Promociones y Productos Financieros",
    "Campañas Comerciales y Sorteos",
    "Educación Financiera y Tips",
    "Eventos y Celebraciones Culturales",
    "Responsabilidad Social y Comunidad",
    "Reconocimientos e Imagen Corporativa",
    "Humor, Tendencias y Cultura Laboral"
]

# Cell 2
# Load the CSV file
df = pd.read_csv('../Extracción/tiktok_01_task.csv')
print(f"Total posts: {len(df)}")
print(f"Columns: {df.columns.tolist()}")
df.head()

# Cell 3
def classify_text(text, index=None):
    """
    Classify a TikTok post text into one of the predefined categories
    """
    try:
        # Print progress
        if index is not None:
            print(f"[{index+1}/{len(df)}] Processing: {text[:50]}...")
        
        prompt = f"""Clasifica el siguiente texto de TikTok en una de estas categorías exactas:
{', '.join(categorias)}

Texto a clasificar: "{text}"

Responde SOLO con una de las categorías de la lista. 
No agregues explicaciones ni texto adicional."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un clasificador de contenido que responde únicamente con la categoría exacta solicitada."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0
        )

        result = response.choices[0].message.content.strip()

        # Validate that the result is in our categories
        if result in categorias:
            print(f"    ✅ Classification: {result}")
            return result
        else:
            print(f"    ⚠️  Invalid result '{result}', using default: Entretenimiento")
            return "Entretenimiento"  # Default category

    except Exception as e:
        print(f"    ❌ Error classifying text: {e}")
        return "Entretenimiento"  # Default category on error

# Cell 4
# Apply classification to all rows
if 'text' in df.columns:
    print(f"Starting classification of {len(df)} posts...\n")
    
    # Apply with progress tracking using enumerate
    classifications = []
    for index, text in enumerate(df['text']):
        classification = classify_text(text, index)
        classifications.append(classification)
    
    df['clase_llm'] = classifications
    
    print("\n🎉 Classification completed!")

    # Show classification distribution
    print("\nClassification distribution:")
    print(df['clase_llm'].value_counts())
else:
    print("Column 'text' not found in the DataFrame")

# Cell 5
# Save the classified data
output_file = 'tiktok_posts_final.csv'
df.to_csv(output_file, index=False, encoding='utf-8')
print(f"Classified data saved to: {output_file}")

# Display first few rows with classification
if 'clase_llm' in df.columns:
    print(df[['text', 'clase_llm']].head(10))
