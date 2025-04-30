export default {
  async fetch(request, env, ctx) {
    // Handle CORS preflight requests
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
      });
    }

    // Only allow GET requests
    if (request.method !== 'GET') {
      return new Response('Method not allowed', { status: 405 });
    }

    try {
      // Get the latest config from KV
      const configsStr = await env.CONFIGS.get('latest_configs');
      
      if (!configsStr) {
        return new Response('No configurations available', { 
          status: 404,
          headers: {
            'Content-Type': 'text/plain',
            'Access-Control-Allow-Origin': '*',
          }
        });
      }

      // Parse the JSON string
      const configsData = JSON.parse(configsStr);
      const configs = JSON.parse(configsData.value);
      
      if (!configs || !configs.length) {
        return new Response('No configurations available', { 
          status: 404,
          headers: {
            'Content-Type': 'text/plain',
            'Access-Control-Allow-Origin': '*',
          }
        });
      }

      // Get the latest config
      const latestConfig = configs[configs.length - 1];

      // Return just the raw config string
      return new Response(latestConfig.config, {
        headers: {
          'Content-Type': 'text/plain',
          'Access-Control-Allow-Origin': '*',
        },
      });
    } catch (error) {
      console.error('Error:', error);
      return new Response('Internal server error', { 
        status: 500,
        headers: {
          'Content-Type': 'text/plain',
          'Access-Control-Allow-Origin': '*',
        }
      });
    }
  },
}; 