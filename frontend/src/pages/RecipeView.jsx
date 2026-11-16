import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { recipesApi } from '../api';

export default function RecipeView() {
  const { id } = useParams();
  const [recipe, setRecipe] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    recipesApi.get(id).then(r => { setRecipe(r.data); setLoading(false); }).catch(() => navigate('/'));
  }, [id, navigate]);

  if (loading) return <p>Загрузка...</p>;
  if (!recipe) return <p>Не найдено</p>;

  return (
    <div className="recipe-view-page">
      <Link to="/" className="back-link">← Назад</Link>
      {recipe.image_url && <img src={recipe.image_url} alt={recipe.title} className="recipe-image" />}
      <h1>{recipe.title}</h1>
      <p className="recipe-description">{recipe.description}</p>
      <div className="recipe-meta">
        <span>🔥 {recipe.calories} ккал</span>
        <span>⏱ {recipe.cook_time} мин</span>
        <span>👤 {recipe.author_name}</span>
      </div>
      <section>
        <h2>Ингредиенты</h2>
        <ul className="ingredients-list">
          {recipe.ingredients.map(i => (
            <li key={i.id}>{i.name} {i.quantity || ''} {i.unit || ''}</li>
          ))}
        </ul>
      </section>
    </div>
  );
}