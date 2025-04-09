import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const WriteBlogPageAlt = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Check if user is logged in
    const fetchUserProfile = async () => {
      try {
        setLoading(true);
        const response = await axios.get('/auth/profile');
        setUser(response.data.user);
        setLoading(false);
      } catch (err) {
        setError('Failed to load user profile. Please log in again.');
        setLoading(false);
        // Redirect to login after a short delay if not authenticated
        setTimeout(() => navigate('/login'), 2000);
      }
    };

    fetchUserProfile();
  }, [navigate]);

  const handleLogout = async () => {
    try {
      await axios.get('/auth/logout');
      setUser(null);
      navigate('/login');
    } catch (err) {
      setError('Failed to logout. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white shadow-lg rounded-lg overflow-hidden">
        <div className="bg-blue-600 p-6 text-white">
          <h1 className="text-2xl font-bold">Welcome to Your Dashboard</h1>
          <p className="mt-1">{user?.email}</p>
        </div>
        
        <div className="p-6">
          <div className="flex items-center mb-6">
            <div className="w-16 h-16 bg-gray-300 rounded-full flex items-center justify-center mr-4">
              {user?.profile_image ? (
                <img 
                  src={user.profile_image} 
                  alt="Profile" 
                  className="w-16 h-16 rounded-full object-cover"
                />
              ) : (
                <span className="text-2xl font-bold text-gray-600">
                  {user?.username?.charAt(0).toUpperCase()}
                </span>
              )}
            </div>
            <div>
              <h2 className="text-xl font-semibold">{user?.username}</h2>
              <p className="text-gray-600">{user?.bio || 'No bio available'}</p>
            </div>
          </div>
          
          <div className="border-t pt-6">
            <h3 className="font-semibold text-lg mb-3">Account Statistics</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-blue-50 p-4 rounded">
                <span className="block text-xl font-bold">{user?.stats?.posts || 0}</span>
                <span className="text-gray-600">Posts</span>
              </div>
              <div className="bg-green-50 p-4 rounded">
                <span className="block text-xl font-bold">{user?.stats?.comments || 0}</span>
                <span className="text-gray-600">Comments</span>
              </div>
            </div>
          </div>
          
          {user?.social_media && (
            <div className="border-t mt-6 pt-6">
              <h3 className="font-semibold text-lg mb-3">Social Media</h3>
              <div className="space-y-2">
                {user.social_media.twitter && (
                  <p className="text-gray-700">
                    <span className="font-medium">Twitter:</span> @{user.social_media.twitter}
                  </p>
                )}
                {user.social_media.instagram && (
                  <p className="text-gray-700">
                    <span className="font-medium">Instagram:</span> @{user.social_media.instagram}
                  </p>
                )}
                {user.social_media.linkedin && (
                  <p className="text-gray-700">
                    <span className="font-medium">LinkedIn:</span> {user.social_media.linkedin}
                  </p>
                )}
              </div>
            </div>
          )}
          
          <div className="mt-8">
            <button 
              onClick={handleLogout}
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WriteBlogPageAlt;