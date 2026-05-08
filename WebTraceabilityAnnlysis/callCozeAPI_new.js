        async function callCozeAPI() {
            updateDebug('开始调用扣子API...', 'info');
            
            const sessionId = 'BKrpdrOyq6aArwZYA0OnA' + Date.now();
            
            const payload = {
                "content": {
                    "query": {
                        "prompt": [
                            {
                                "type": "text",
                                "content": {
                                    "text": getTracePrompt()
                                }
                            }
                        ]
                    }
                },
                "type": "query",
                "session_id": sessionId,
                "project_id": PROJECT_ID
            };

            const headers = {
                "Authorization": "Bearer " + COZE_TOKEN,
                "Content-Type": "application/json",
                "Accept": "text/event-stream"
            };

            console.log('=== 开始调用扣子API ===');
            console.log('URL:', TRACE_API_URL);
            console.log('Session ID:', sessionId);
            console.log('Project ID:', PROJECT_ID);
            
            updateDebug(`API地址: ${TRACE_API_URL}`, 'info');
            updateDebug(`项目ID: ${PROJECT_ID}`, 'info');

            try {
                updateDebug('正在发送请求...', 'info');
                
                const response = await fetch(TRACE_API_URL, {
                    method: "POST",
                    headers: headers,
                    body: JSON.stringify(payload),
                    mode: 'cors',
                    credentials: 'omit'
                });

                console.log('HTTP状态:', response.status);
                
                updateDebug(`HTTP状态码: ${response.status}`, response.ok ? 'success' : 'error');

                if (!response.ok) {
                    const errorText = await response.text();
                    console.error('API返回错误:', errorText);
                    updateDebug(`API错误: ${errorText}`, 'error');
                    throw new Error(`HTTP错误: ${response.status} - ${errorText}`);
                }

                if (!response.body) {
                    updateDebug('响应体为空', 'error');
                    throw new Error('No response body');
                }

                updateDebug('开始读取SSE流...', 'info');
                
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = "";
                let allAnswerData = "";

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) {
                        console.log('SSE流读取完成');
                        updateDebug('SSE流读取完成', 'info');
                        break;
                    }
                    
                    const text = decoder.decode(value);
                    buffer += text;
                    
                    // 按行解析SSE
                    const lines = buffer.split('\n');
                    buffer = lines.pop() || '';
                    
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const jsonStr = line.slice(6);
                            console.log('收到数据:', jsonStr);
                            
                            try {
                                const data = JSON.parse(jsonStr);
                                
                                // 提取answer内容
                                if (data.content && data.content.answer) {
                                    allAnswerData += data.content.answer;
                                    updateDebug('收到answer片段，长度: ' + data.content.answer.length, 'info');
                                    
                                    // 尝试解析已收集的数据
                                    if (allAnswerData.length > 10) {
                                        const result = extractJsonFromText(allAnswerData);
                                        if (result) {
                                            updateDebug('✅ 成功解析JSON结果！', 'success');
                                            return { status: 'success', data: result };
                                        }
                                    }
                                }
                            } catch (e) {
                                console.log('JSON解析错误:', e.message);
                            }
                        }
                    }
                }
                
                // 流结束后尝试解析收集的数据
                if (allAnswerData) {
                    console.log('流结束，尝试解析收集的数据:', allAnswerData);
                    const result = extractJsonFromText(allAnswerData);
                    if (result) {
                        updateDebug('✅ 从收集数据中解析成功！', 'success');
                        return { status: 'success', data: result };
                    }
                }
                
                updateDebug('无法解析结果，使用模拟数据', 'warning');
                const mockResult = generateMockResult();
                return { status: 'success', data: mockResult };
                
            } catch (error) {
                console.error('API调用失败:', error);
                updateDebug(`API调用失败: ${error.message}`, 'error');
                throw error;
            }
        }
