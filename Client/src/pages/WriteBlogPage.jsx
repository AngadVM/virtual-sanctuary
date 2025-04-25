import React, { useState, useEffect } from 'react';
import PostCard from '@components/PostCard';
import ClerkAuth from '@components/ClerkAuth';
import { useUser } from '@clerk/clerk-react';
import PostDetailsModal from './PostDetailsModal'; // Import the new modal component

function WriteBlogPage() {
  const { isSignedIn, user } = useUser();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const [selectedPost, setSelectedPost] = useState(null);
  const [newPost, setNewPost] = useState({
    title: '',
    postText: '',
    imageUrl: ''
  });

  const [posts, setPosts] = useState([
    {
      id: 1,
      author: "@wildclicker",
      title: "Shy Climbers of the Eastern Himalayas",
      postText: "Red pandas are native to the Eastern Himalayas and southwestern China. They live in temperate forests and are mostly active at dusk and dawn. With a diet mainly of bamboo, they are excellent climbers and solitary by nature. Sadly, they're endangered due to habitat loss.",
      likeCount: 42,
      shareCount: 12,
      imageUrl: "https://images.pexels.com/photos/1210229/pexels-photo-1210229.jpeg",
      timestamp: "2 hours ago"
    },
    {
      id: 2,
      author: "@wonderlife",
      title: "Majestic Dancers of African Wetlands",
      postText: "Native to eastern and southern Africa, these elegant birds are known for their golden crown and striking courtship dances. They thrive in grasslands and wetlands, often nesting in tall vegetation near water bodies.",
      likeCount: 67,
      shareCount: 24,
      imageUrl: "https://images.pexels.com/photos/45853/grey-crowned-crane-bird-crane-animal-45853.jpeg?auto=compress&cs=tinysrgb&w=600",
      timestamp: "5 hours ago"
    },
    {
      id: 3,
      author: "@clickista",
      title: "Bright River Hunters with Swift Precision",
      postText: "Found across Asia, Africa, and Europe near rivers and lakes, kingfishers are known for their colorful feathers and dive-hunting skills. They feed mainly on fish, insects, and amphibians, using their sharp beaks.",
      likeCount: 89,
      shareCount: 36,
      imageUrl: "https://images.pexels.com/photos/326900/pexels-photo-326900.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
      timestamp: "8 hours ago"
    },
    {
      id: 4,
      author: "@insanicks",
      title: "Flightless Birds of the Southern Ice",
      postText: "Mostly found in the Southern Hemisphere, especially Antarctica, penguins are excellent swimmers adapted to cold climates. They waddle on land but are agile underwater, feeding on fish and krill.",
      likeCount: 124,
      shareCount: 57,
      imageUrl: "https://images.pexels.com/photos/52509/penguins-emperor-antarctic-life-52509.jpeg?auto=compress&cs=tinysrgb&w=600",
      timestamp: "1 day ago"
    },
    {
      id: 5,
      author: "@lovewildlife",
      title: "India's Fierce Forest Guardian",
      postText: "Found in India, Bangladesh, and Nepal, Bengal tigers roam dense forests and mangroves. As solitary hunters, they are powerful and stealthy predators. These majestic cats are endangered due to poaching and habitat loss.",
      likeCount: 76,
      shareCount: 29,
      imageUrl: "https://images.pexels.com/photos/2529296/pexels-photo-2529296.jpeg?auto=compress&cs=tinysrgb&w=600",
      timestamp: "2 days ago"
    }
  ]);

  const [tags] = useState(['#mammals', '#birds', '#reptiles', '#insects', '#seaside', '#endangered']);
  
  const [recommendations] = useState([
    {
      id: 101,
      author: "@influencer",
      title: "Tropical Tree Climber",
      imageUrl: "https://images.pexels.com/photos/26600110/pexels-photo-26600110/free-photo-of-iguana-lying-on-rocks.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
      readTime: "5 min read"
    },
    {
      id: 102,
      author: "@mindfulness",
      title: "Himalayan Forest Dweller",
      imageUrl: "https://images.pexels.com/photos/30395793/pexels-photo-30395793/free-photo-of-charming-red-panda-climbing-in-natural-habitat.jpeg?auto=compress&cs=tinysrgb&w=600",
      readTime: "3 min read"
    },
    {
      id: 103,
      author: "@bookworm",
      title: "Playful Ocean Swimmers",
      imageUrl: "https://images.pexels.com/photos/6735397/pexels-photo-6735397.jpeg?auto=compress&cs=tinysrgb&w=600",
      readTime: "7 min read"
    },
    {
      id: 104,
      author: "@fitnessguru",
      title: "Tiny Armored Insect",
      imageUrl: "https://images.pexels.com/photos/30465401/pexels-photo-30465401/free-photo-of-colorful-beetle-on-leaf-nature-macro-photography.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
      readTime: "4 min read"
    }
  ]);

  // Check for user's theme preference when component mounts
  useEffect(() => {
    // Check for system preference or saved preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      setDarkMode(true);
      document.documentElement.classList.add('dark');
    } else {
      setDarkMode(false);
      document.documentElement.classList.remove('dark');
    }
  }, []);

  // Update theme when darkMode state changes
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [darkMode]);

  // Prevent scrolling when modal is open
  useEffect(() => {
    if (selectedPost) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [selectedPost]);

  const toggleDarkMode = () => {
    setDarkMode(prevMode => !prevMode);
  };

  const handleNewPostChange = (e) => {
    const { name, value } = e.target;
    setNewPost(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmitNewPost = (e) => {
    e.preventDefault();
    
    // Get the user's username or create a default one
    let authorUsername = "@guest";
    
    // Update the author with the logged in user's username if available
    if (isSignedIn && user) {
      // Try to get the username, or use their first part of email as a fallback
      const username = user.username || user.primaryEmailAddress?.emailAddress.split('@')[0];
      authorUsername = username ? `@${username}` : `@user${user.id.substring(0, 6)}`;
    }
    
    // Create new post with current date/time and default values
    const newPostItem = {
      id: posts.length + 1,
      author: authorUsername,
      title: newPost.title,
      postText: newPost.postText,
      likeCount: 0,
      shareCount: 0,
      imageUrl: newPost.imageUrl || 'https://images.pexels.com/photos/814898/pexels-photo-814898.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1',
      timestamp: "Just now"
    };
    
    // Add new post to the beginning of the posts array
    setPosts(prevPosts => [newPostItem, ...prevPosts]);
    
    // Reset form and close dialog
    setNewPost({
      title: '',
      postText: '',
      imageUrl: ''
    });
    setIsDialogOpen(false);
  };

  // Handle post card click
  const handlePostCardClick = (post) => {
    setSelectedPost(post);
  };

  // Handle recommendation click
  const handleRecommendationClick = (recommendation) => {
    setSelectedPost(recommendation);
  };

  // Close modal
  const closeModal = () => {
    setSelectedPost(null);
  };

  return (
    <div className={`${darkMode ? 'dark bg-gray-900 text-white' : 'bg-white text-gray-900'} min-h-screen transition-colors duration-300`}>
      <div className="container mx-auto px-4 py-6">
        <header className="mb-6 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex w-full md:w-auto gap-2 items-center">
            <button className={`flex flex-grow justify-start items-center border ${darkMode ? 'border-gray-600 text-gray-300' : 'border-gray-400 text-gray-400'} p-3 rounded-full`}>
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <span className="pl-2">Search for posts...</span>
            </button>
            <button 
              onClick={toggleDarkMode} 
              className={`p-3 rounded-full ${darkMode ? 'bg-gray-700 text-yellow-300' : 'bg-gray-200 text-gray-700'} transition-colors`}
              aria-label={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {darkMode ? (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                </svg>
              )}
            </button>
          </div>
          <div className="flex gap-8">
            <button 
              className="bg-green-500 font-medium ring-1 ring-green-600 text-white px-3 py-1.5 rounded-full hover:bg-green-500 transition-colors hover:cursor-pointer"
              onClick={() => setIsDialogOpen(true)}
            >
            &#x2b;  New Post
            </button>
            <ClerkAuth />
          </div>
        </header>

        {/* New Post Dialog */}
        {isDialogOpen && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className={`${darkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'} rounded-lg p-6 w-full max-w-md mx-4`}>
              <h2 className="text-2xl font-bold mb-4">Create New Post</h2>
              {!isSignedIn && (
                <div className="mb-4 p-3 bg-yellow-100 text-yellow-800 rounded-md">
                  You're not signed in. Your post will be published as a guest.
                </div>
              )}
              <form onSubmit={handleSubmitNewPost}>
                <div className="mb-4">
                  <label htmlFor="title" className={`block ${darkMode ? 'text-gray-200' : 'text-gray-700'} font-medium mb-2`}>Title</label>
                  <input
                    type="text"
                    id="title"
                    name="title"
                    value={newPost.title}
                    onChange={handleNewPostChange}
                    className={`w-full border ${darkMode ? 'border-gray-600 bg-gray-700 text-white' : 'border-gray-300 bg-white text-gray-900'} rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500`}
                    required
                  />
                </div>
                
                <div className="mb-4">
                  <label htmlFor="postText" className={`block ${darkMode ? 'text-gray-200' : 'text-gray-700'} font-medium mb-2`}>Content</label>
                  <textarea
                    id="postText"
                    name="postText"
                    value={newPost.postText}
                    onChange={handleNewPostChange}
                    className={`w-full border ${darkMode ? 'border-gray-600 bg-gray-700 text-white' : 'border-gray-300 bg-white text-gray-900'} rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-24`}
                    required
                  ></textarea>
                </div>
                
                <div className="mb-4">
                  <label htmlFor="imageUrl" className={`block ${darkMode ? 'text-gray-200' : 'text-gray-700'} font-medium mb-2`}>Image URL (optional)</label>
                  <input
                    type="text"
                    id="imageUrl"
                    name="imageUrl"
                    value={newPost.imageUrl}
                    onChange={handleNewPostChange}
                    className={`w-full border ${darkMode ? 'border-gray-600 bg-gray-700 text-white' : 'border-gray-300 bg-white text-gray-900'} rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500`}
                  />
                </div>
                
                <div className="flex justify-end gap-3 mt-6">
                  <button
                    type="button"
                    className={`px-4 py-2 border ${darkMode ? 'border-gray-600 hover:bg-gray-700' : 'border-gray-300 hover:bg-gray-100'} rounded-md transition-colors`}
                    onClick={() => setIsDialogOpen(false)}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-700 text-white rounded-md hover:bg-blue-800 transition-colors"
                  >
                    Publish
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        <div className="flex flex-wrap gap-2 mb-6">
          {tags.map((tag, index) => (
            <span
              key={index}
              className={`${darkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-700/70 hover:bg-gray-500'} text-white px-3 py-1 rounded-xl text-sm transition-colors cursor-pointer`}
            >
              {tag}
            </span>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="lg:col-span-3">
            <h2 className="text-3xl md:text-4xl font-extrabold mb-6">POSTS</h2>
            <div className="space-y-6">
              {posts.map(post => (
                <PostCard
                  key={post.id}
                  author={post.author}
                  title={post.title}
                  postText={post.postText}
                  likeCount={post.likeCount}
                  shareCount={post.shareCount}
                  imageUrl={post.imageUrl}
                  timestamp={post.timestamp}
                  darkMode={darkMode}
                  onCardClick={() => handlePostCardClick(post)}
                />
              ))}
            </div>
          </div>

          <div className="lg:col-span-1">
            <div className={`${darkMode ? 'bg-gray-800' : 'bg-gray-100'} p-4 rounded-lg sticky top-4`}>
              <h3 className="text-xl font-semibold mb-4">Recommended</h3>
              <div className="space-y-4">
                {recommendations.map(rec => (
                  <div 
                    key={rec.id} 
                    className={`${darkMode ? 'bg-gray-700' : 'bg-white'} rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow cursor-pointer`}
                    onClick={() => handleRecommendationClick(rec)}
                  >
                    <img src={rec.imageUrl} alt={rec.title} className="w-full h-32 object-cover" />
                    <div className="p-3">
                      <h4 className="font-medium text-lg">{rec.title}</h4>
                      <div className="flex justify-between items-center mt-2 text-sm text-gray-500">
                        <span>{rec.author}</span>
                        <span>{rec.readTime}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-6">
                <h4 className="font-medium mb-3">Popular Tags</h4>
                <div className="flex flex-wrap gap-2">
                  {tags.slice(0, 4).map((tag, index) => (
                    <span 
                      key={index} 
                      className={`text-sm ${darkMode ? 'text-gray-300 bg-gray-700 hover:bg-gray-600' : 'text-gray-600 bg-gray-200 hover:bg-gray-300'} px-2 py-1 rounded cursor-pointer`}
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Post Details Modal */}
      {selectedPost && (
        <PostDetailsModal 
          post={selectedPost} 
          darkMode={darkMode} 
          onClose={closeModal} 
        />
      )}
    </div>
  );
}

export default WriteBlogPage;