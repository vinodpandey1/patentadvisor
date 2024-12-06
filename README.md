# patentadvisor

## 1. patent-app 
This is for UI code repository of AI Patent Advisor Portal 

### How to run 
#### UI Deployment Plan

1. Checkout the code from Github https://github.com/dkhandelwal3/patentadvisor
2. Install NodeJs v18.20.4 and npm v10.7.0
3. Supabase - Setting up user authentication 
   - Magic Link Login - To enable magic link login
     - In your Supabase dashboard, configure the URL redirect settings:
       - Go to “Authentication” then “URL Configuration”
       - Add your site URL (use localhost for development or your production URL for live sites)
       - Add http://localhost:3000/* or your production URL as “Redirect URLs”
4. Google Auth
   - To set up Google Auth
     - Configure settings in the Google Cloud Console
     - Add the obtained keys to Supabase providers(Follow the steps under Google pre-built configuration)
5. Storage
    - Set up Cloudflare R2
      - Create a bucket
      - Enable public access
      - Get API keys and other information
6. Analytics 
   - Setting up PostHog Analytics to understand user behavior
     - Create a PostHog account or sign in.
     - Create a new project
     - Get an API_KEY and a HOST
7. Create .env file from .env.example and provide all keys for LLM, Supabase, PostHog and S3 connectivity
8. Navigate to patent-app
9. Install dependencies - npm install
10. Execute npm run dev - it typically runs the dev script defined in project's package.json file. For a Next.js application, this script usually invokes the Next.js development server.


## 2. patent-service 
This is for backend services and all agents 

### How to run 

#### Backend Deployment Plan
1. Checkout the code from Github https://github.com/dkhandelwal3/patentadvisor
2. Install python3 (3.11) and other utilities related to unstructure.io as mentioned in https://python.langchain.com/docs/integrations/providers/unstructured/
3. Navigate to patent-service
4. Create virtual environment and activate the environment
5. Create .env file from .env.example and provide all keys for LLM, Supabase and S3 connectivity
6. Install the libraries using pip from requirements.txt
7. Use python to run the Back end API : python3 -m src.controller.app

