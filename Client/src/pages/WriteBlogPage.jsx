import React, { useState } from 'react'
import PostCard from '@components/PostCard'

function WriteBlogPage() {
  const [posts, setPosts] = useState([
    {
      id: 1,
      author: "@johndoe",
      title: "Future of Technology",
      postText: "Exploring the transformative potential of emerging technologies in our rapidly changing world.",
      likeCount: 42,
      shareCount: 12,
      imageUrl: "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1471&q=80"
    },
    {
      id: 2,
      author: "@janedoe",
      title: "Climate Change Insights",
      postText: "A comprehensive look at the current state of global climate and potential solutions.",
      likeCount: 67,
      shareCount: 24,
      imageUrl: "https://images.unsplash.com/photo-1541873676-2218a1a4c5c2?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1518&q=80"
    },
    {
      id: 3,
      author: "@techguru",
      title: "AI Revolution",
      postText: "Examining the impact of artificial intelligence on various industries and society.",
      likeCount: 89,
      shareCount: 36,
      imageUrl: "https://images.unsplash.com/photo-1517180102447-cce43c2dab5a?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1470&q=80"
    }
  ]);

  const [tags] = useState(['#technology', '#climate', '#AI']);

  const handleNewPost = () => {
    // Placeholder for new post creation logic
    alert('New Post functionality to be implemented');
  };

  return (
    <div className="container mx-auto px-4 py-6">
      <header className="font-bold mb-4 flex justify-between items-center">
        <button className='flex w-xl justify-start items-center border-1 font-medium   border-gray-400 p-3 rounded-3xl text-gray-400'>
          <svg xmlns="http://www.w3.org/2000/svg" x="0px" y="0px" width="24" height="24" viewBox="0 0 50 50">
            <path d="M 21 3 C 11.621094 3 4 10.621094 4 20 C 4 29.378906 11.621094 37 21 37 C 24.710938 37 28.140625 35.804688 30.9375 33.78125 L 44.09375 46.90625 L 46.90625 44.09375 L 33.90625 31.0625 C 36.460938 28.085938 38 24.222656 38 20 C 38 10.621094 30.378906 3 21 3 Z M 21 5 C 29.296875 5 36 11.703125 36 20 C 36 28.296875 29.296875 35 21 35 C 12.703125 35 6 28.296875 6 20 C 6 11.703125 12.703125 5 21 5 Z"></path>
          </svg>
          <span className='pl-2'>Search for posts...</span></button>
        <button
          onClick={handleNewPost}
          className="bg-black text-white px-4 py-2 rounded-md hover:bg-gray-800 transition-colors"
        >

          New Post
        </button>
      </header>

      <div className="flex space-x-2 mb-4">
        {tags.map((tag, index) => (
          <span
            key={index}
            className="bg-gray-400 text-white px-3 py-1 rounded-xl text-sm"
          >
            {tag}
          </span>
        ))}
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="col-span-3">
          <h2 className="text-4xl font-extrabold mb-4">POSTS</h2>
          <div className="space-y-4">
            {posts.map(post => (
              <PostCard
                key={post.id}
                author={post.author}
                title={post.title}
                postText={post.postText}
                likeCount={post.likeCount}
                shareCount={post.shareCount}
                imageUrl={post.imageUrl}
              />
            ))}
          </div>
        </div>

        <div className="col-span-1 bg-gray-100 p-4 rounded-lg">
          <h3 className="text-xl font-semibold mb-3">Recommended</h3>
          {/* Optional: Add recommended posts or content */}
          <p className="text-gray-600">Stay tuned for recommended content!</p>
        </div>
      </div>
    </div>
  );
}

export default WriteBlogPage