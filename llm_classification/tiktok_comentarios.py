### CLASIFICACIÓN DE COMENTARIOS DE TIKTOK USANDO LLM ###

import pandas as pd
import os
from dotenv import load_dotenv
from openai import OpenAI
import re
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define sentiment categories
sentiment_categories = [
    "positivo",
    "neutral", 
    "sarcástico",
    "negativo"
]

# Define Plutchik's Wheel of Emotions categories
plutchik_emotions = [
    "alegría",
    "confianza", 
    "miedo",
    "sorpresa",
    "tristeza",
    "disgusto",
    "ira",
    "anticipación"
]

def extract_author_from_url(video_url):
    """
    Extract author name from TikTok video URL
    """
    try:
        # Extract @username from URL like https://www.tiktok.com/@caja.piura/video/...
        match = re.search(r'@([^/]+)', video_url)
        if match:
            return match.group(1)
        return "unknown"
    except:
        return "unknown"

def classify_sentiment(text, index=None, total=None):
    """
    Classify comment sentiment using OpenAI
    """
    try:
        # Print progress
        if index is not None and total is not None:
            print(f"[{index+1}/{total}] Clasificando sentimiento: {text[:50]}...")
        
        prompt = f"""Clasifica el sentimiento del siguiente comentario de TikTok en una de estas categorías exactas:
{', '.join(sentiment_categories)}

Comentario: "{text}"

Responde SOLO con una de las categorías de la lista. No agregues explicaciones ni texto adicional."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un clasificador de sentimientos que responde únicamente con la categoría exacta solicitada."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0
        )
        
        result = response.choices[0].message.content.strip().lower()
        
        # Validate that the result is in our categories
        if result in sentiment_categories:
            print(f"    ✅ Sentimiento: {result}")
            return result
        else:
            print(f"    ⚠️  Resultado inválido '{result}', usando default: neutral")
            return "neutral"  # Default category

    except Exception as e:
        print(f"    ❌ Error clasificando sentimiento: {e}")
        return "neutral"  # Default category on error

def classify_emotion(text, index=None, total=None):
    """
    Classify comment emotion using Plutchik's Wheel of Emotions
    """
    try:
        # Print progress
        if index is not None and total is not None:
            print(f"[{index+1}/{total}] Clasificando emoción: {text[:50]}...")
        
        prompt = f"""Clasifica la emoción del siguiente comentario de TikTok según la Rueda de las Emociones de Plutchik en una de estas categorías exactas:
{', '.join(plutchik_emotions)}

Comentario: "{text}"

Responde SOLO con una de las emociones de la lista. No agregues explicaciones ni texto adicional."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un clasificador de emociones basado en la Rueda de Plutchik que responde únicamente con la emoción exacta solicitada."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0
        )
        
        result = response.choices[0].message.content.strip().lower()
        
        # Validate that the result is in our categories
        if result in plutchik_emotions:
            print(f"    ✅ Emoción: {result}")
            return result
        else:
            print(f"    ⚠️  Resultado inválido '{result}', usando default: neutral")
            return "neutral"  # Default for emotions too

    except Exception as e:
        print(f"    ❌ Error clasificando emoción: {e}")
        return "neutral"  # Default category on error

def main():
    # Load the CSV file
    print("📂 Cargando datos de comentarios...")
    try:
        df = pd.read_csv('../Extracción/tiktok_task_comments_20250830_162816.csv')
        print(f"✅ Datos cargados: {len(df)} comentarios")
        print(f"📋 Columnas: {df.columns.tolist()}")
    except Exception as e:
        print(f"❌ Error cargando datos: {e}")
        return

    # Extract author from videoWebUrl
    print("\n🔍 Extrayendo autores de las URLs...")
    df['video_author'] = df['videoWebUrl'].apply(extract_author_from_url)
    unique_authors = df['video_author'].nunique()
    print(f"✅ Autores únicos extraídos: {unique_authors}")
    print(f"👥 Autores: {df['video_author'].unique()[:10]}")  # Show first 10

    # Display basic stats
    print(f"\n📊 Estadísticas básicas:")
    print(f"   • Total comentarios: {len(df)}")
    print(f"   • Comentarios únicos: {df['text'].nunique()}")
    print(f"   • Promedio likes por comentario: {df['diggCount'].mean():.1f}")
    print(f"   • Comentarios con replies: {df['replyCommentTotal'].notna().sum()}")

    # Sample first few comments for verification
    print(f"\n📝 Primeros 3 comentarios:")
    for i, row in df.head(3).iterrows():
        print(f"   {i+1}. [{row['video_author']}] {row['text'][:100]}...")

    # Start classification process
    total_comments = len(df)
    print(f"\n🚀 Iniciando clasificación de {total_comments} comentarios...")
    print("=" * 60)

    # Classify sentiments
    print("\n🎭 CLASIFICANDO SENTIMIENTOS...")
    sentiments = []
    for index, text in enumerate(df['text']):
        if pd.notna(text) and str(text).strip():
            sentiment = classify_sentiment(str(text), index, total_comments)
            sentiments.append(sentiment)
        else:
            sentiments.append("neutral")
            print(f"[{index+1}/{total_comments}] ⚠️  Texto vacío, asignando neutral")
    
    df['sentimiento'] = sentiments
    print(f"\n✅ Sentimientos clasificados!")
    print("📊 Distribución de sentimientos:")
    sentiment_dist = df['sentimiento'].value_counts()
    for sentiment, count in sentiment_dist.items():
        print(f"   • {sentiment}: {count} ({count/len(df)*100:.1f}%)")

    print("\n" + "=" * 60)

    # Classify emotions
    print("\n🎨 CLASIFICANDO EMOCIONES (PLUTCHIK)...")
    emotions = []
    for index, text in enumerate(df['text']):
        if pd.notna(text) and str(text).strip():
            emotion = classify_emotion(str(text), index, total_comments)
            emotions.append(emotion)
        else:
            emotions.append("neutral")
            print(f"[{index+1}/{total_comments}] ⚠️  Texto vacío, asignando neutral")
    
    df['emocion_plutchik'] = emotions
    print(f"\n✅ Emociones clasificadas!")
    print("📊 Distribución de emociones:")
    emotion_dist = df['emocion_plutchik'].value_counts()
    for emotion, count in emotion_dist.items():
        print(f"   • {emotion}: {count} ({count/len(df)*100:.1f}%)")

    print("\n" + "=" * 60)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f'tiktok_comentarios_clasificados_{timestamp}.csv'
    
    # Add some summary columns
    df['comment_length'] = df['text'].astype(str).str.len()
    df['has_mentions'] = df['mentions'].apply(lambda x: len(eval(str(x))) > 0 if pd.notna(x) else False)
    
    df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"💾 Datos guardados en: {output_file}")
    print(f"\n🎉 CLASIFICACIÓN COMPLETADA!")
    
    # Final summary
    print(f"\n📈 RESUMEN FINAL:")
    print(f"   • Total comentarios procesados: {len(df)}")
    print(f"   • Autores de video únicos: {df['video_author'].nunique()}")
    print(f"   • Sentimiento más común: {sentiment_dist.index[0]} ({sentiment_dist.iloc[0]} comentarios)")
    print(f"   • Emoción más común: {emotion_dist.index[0]} ({emotion_dist.iloc[0]} comentarios)")
    print(f"   • Archivo guardado: {output_file}")

if __name__ == "__main__":
    main()
