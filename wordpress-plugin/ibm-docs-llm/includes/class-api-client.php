<?php
/**
 * API Client for IBM Docs LLM Backend
 */

class IBM_Docs_LLM_API_Client {
    
    /**
     * API URL
     */
    private $api_url;
    
    /**
     * API Key
     */
    private $api_key;
    
    /**
     * Constructor
     */
    public function __construct($api_url = null, $api_key = null) {
        $this->api_url = $api_url ?: get_option('ibm_docs_llm_api_url', '');
        $this->api_key = $api_key ?: get_option('ibm_docs_llm_api_key', '');
    }
    
    /**
     * Send chat request to backend API
     */
    public function send_chat_request($question, $conversation_id = null, $max_tokens = 1000) {
        if (empty($this->api_url) || empty($this->api_key)) {
            return new WP_Error(
                'missing_config',
                __('API URL or API Key is not configured', 'ibm-docs-llm')
            );
        }
        
        $endpoint = trailingslashit($this->api_url) . 'api/chat';
        
        $body = array(
            'question' => $question,
            'max_tokens' => $max_tokens
        );
        
        if ($conversation_id) {
            $body['conversation_id'] = $conversation_id;
        }
        
        $response = wp_remote_post($endpoint, array(
            'headers' => array(
                'Authorization' => 'Bearer ' . $this->api_key,
                'Content-Type' => 'application/json'
            ),
            'body' => json_encode($body),
            'timeout' => 30,
            'sslverify' => true
        ));
        
        if (is_wp_error($response)) {
            return $response;
        }
        
        $status_code = wp_remote_retrieve_response_code($response);
        $body = wp_remote_retrieve_body($response);
        
        if ($status_code !== 200) {
            $error_data = json_decode($body, true);
            return new WP_Error(
                'api_error',
                $error_data['detail'] ?? __('API request failed', 'ibm-docs-llm'),
                array('status' => $status_code)
            );
        }
        
        $data = json_decode($body, true);
        
        if (json_last_error() !== JSON_ERROR_NONE) {
            return new WP_Error(
                'json_error',
                __('Failed to parse API response', 'ibm-docs-llm')
            );
        }
        
        return $data;
    }
    
    /**
     * Test API connection
     */
    public function test_connection() {
        if (empty($this->api_url) || empty($this->api_key)) {
            return array(
                'success' => false,
                'message' => __('API URL or API Key is not configured', 'ibm-docs-llm')
            );
        }
        
        $endpoint = trailingslashit($this->api_url) . 'api/health';
        
        $response = wp_remote_get($endpoint, array(
            'timeout' => 10,
            'sslverify' => true
        ));
        
        if (is_wp_error($response)) {
            return array(
                'success' => false,
                'message' => $response->get_error_message()
            );
        }
        
        $status_code = wp_remote_retrieve_response_code($response);
        
        if ($status_code !== 200) {
            return array(
                'success' => false,
                'message' => sprintf(__('API returned status code: %d', 'ibm-docs-llm'), $status_code)
            );
        }
        
        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);
        
        return array(
            'success' => true,
            'message' => __('Connection successful!', 'ibm-docs-llm'),
            'data' => $data
        );
    }
    
    /**
     * Get API statistics
     */
    public function get_statistics() {
        if (empty($this->api_url) || empty($this->api_key)) {
            return new WP_Error(
                'missing_config',
                __('API URL or API Key is not configured', 'ibm-docs-llm')
            );
        }
        
        $endpoint = trailingslashit($this->api_url) . 'api/sources';
        
        $response = wp_remote_get($endpoint, array(
            'headers' => array(
                'Authorization' => 'Bearer ' . $this->api_key
            ),
            'timeout' => 10,
            'sslverify' => true
        ));
        
        if (is_wp_error($response)) {
            return $response;
        }
        
        $status_code = wp_remote_retrieve_response_code($response);
        $body = wp_remote_retrieve_body($response);
        
        if ($status_code !== 200) {
            return new WP_Error(
                'api_error',
                __('Failed to get statistics', 'ibm-docs-llm')
            );
        }
        
        return json_decode($body, true);
    }
}

// Made with Bob
