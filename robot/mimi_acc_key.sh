HOME=/home/mark/pics
curl -X POST https://auth.mimi.fd.ai/v2/token \
-F grant_type="https://auth.mimi.fd.ai/grant_type/client_credentials" \
-F client_id="7fce6419408c4c9186e95c3a19e77368:5f68968174704e549ec926e1c2f8dbf1" \
-F client_secret="de9c93a3f468dadb58722e70c5ab071f33d55a6d25466c19e1cf28d106afaa1250d33343355f369cfcb54f9c61087af17beef5cdf256c989a88f17f2fc52d858862b331a0ffeb8bd0074e952e5c4df1df8bb359ac8ec9c7bb7272a6e256d00ed19fce35e8c35a9576515e485287de34499cd36565cfe5d1c18139f69c7b0b4125c8eaac2834283ac2752580d892f237aaa464ac1c4b55dbd31b4134d488a53ac19d0dda3ed2a4fca9b82fe05a19a6bda0c3324f4063fccd4268f063020dca2147a29059b56f056c526759af410177913c904fe4232dd88ad7c6b3b6dc640dc268edeb10bfa722e62e465ca16b61152184c322d0d3e562d6e1c86e612ef00a681" \
--form-string scope="https://apis.mimi.fd.ai/auth/asr/http-api-service;https://apis.mimi.fd.ai/auth/asr/websocket-api-service;https://apis.mimi.fd.ai/auth/nict-asr/http-api-service;https://apis.mimi.fd.ai/auth/nict-asr/websocket-api-service;https://apis.mimi.fd.ai/auth/nict-tts/http-api-service;https://apis.mimi.fd.ai/auth/nict-tra/http-api-service" > $HOME/mimi.api
cat $HOME/mimi.api
# replies on success with {"operationId": "123c1ecd75c74346a0432915a734b051", "startTimestamp": 1615738629, "selfLink": "https://auth.mimi.fd.ai/v2/operations/123c1ecd75c74346a0432915a734b051", "progress": 100, "code": 200, "kind": "auth#operation#accesstoken", "endTimestamp": 1615738629, "status": "success", "error": "", "targetLink": "", "accessToken": "d70a3586-e6fa-48c6-8f02-550f25cfc423", "expires_in": 3600}
