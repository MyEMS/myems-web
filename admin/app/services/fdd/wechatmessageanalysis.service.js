'use strict';
app.factory('WechatMessageAnalysisService', function($http) {
    return {
        getAnalysisResult: function(query, headers, callback) {
            $http.get(getAPI()+"wechatmessages"+"/from/"+query.datestart+"/to/"+query.dateend, {headers})
            .then(function (response) {
                callback(response);
            }, function (response) {
                callback(response);
            });
        },

        deleteWechatMessage: function(wechatmessage, headers, callback) {
            $http.delete(getAPI()+'wechatmessages/'+wechatmessage.id, {headers})
            .then(function (response) {
                callback(response);
            }, function (response) {
                callback(response);
            });
        }

    };
});
