'use strict';
app.factory('EnergyStorageContainerPowerconversionsystemService', function($http) {
    return {
        getAllEnergyStorageContainerPowerconversionsystems: function(headers, callback) {
            $http.get(getAPI()+'energystoragecontainerpowerconversionsystems', {headers})
            .then(function (response) {
                callback(response);
            }, function (response) {
                callback(response);
            });
        },
        getEnergyStorageContainerPowerconversionsystemsByEnergyStorageContainerID: function(id, headers, callback) {
            $http.get(getAPI()+'energystoragecontainers/'+id+'/powerconversionsystems', {headers})
            .then(function (response) {
                callback(response);
            }, function (response) {
                callback(response);
            });
        },
        addEnergyStorageContainerPowerconversionsystem: function(id, energystoragecontainerpowerconversionsystem, headers, callback) {
            $http.post(getAPI()+'energystoragecontainers/'+id+'/powerconversionsystems',{data:energystoragecontainerpowerconversionsystem}, {headers})
            .then(function (response) {
                callback(response);
            }, function (response) {
                callback(response);
            });
        },
        editEnergyStorageContainerPowerconversionsystem: function(id, energystoragecontainerpowerconversionsystem, headers, callback) {
            $http.put(getAPI()+'energystoragecontainers/'+id+'/powerconversionsystems/'+energystoragecontainerpowerconversionsystem.id,{data:energystoragecontainerpowerconversionsystem}, {headers})
            .then(function (response) {
                callback(response);
            }, function (response) {
                callback(response);
            });
        },
        deleteEnergyStorageContainerPowerconversionsystem: function(id, energystoragecontainerpowerconversionsystemyID, headers, callback) {
            $http.delete(getAPI()+'energystoragecontainers/'+id+'/powerconversionsystems/'+energystoragecontainerpowerconversionsystemyID, {headers})
            .then(function (response) {
                callback(response);
            }, function (response) {
                callback(response);
            });
        },
    };
});
