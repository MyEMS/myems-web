'use strict';
app.controller('ApiKeyController', function (
    $scope,
	$window,
	$uibModal,
	ApiKeyService,
	toaster,
	$translate,
	SweetAlert) {
	$scope.cur_user = JSON.parse($window.localStorage.getItem("myems_admin_ui_current_user"));
	$scope.getAllApiKeys = function () {
		let headers = { "User-UUID": $scope.cur_user.uuid, "Token": $scope.cur_user.token };
		ApiKeyService.getAllApiKeys(headers, function (response) {
			if (angular.isDefined(response.status) && response.status === 200) {
				$scope.apiKeys = response.data;
			} else {
				$scope.apiKeys = [];
			}
		});

	};

	$scope.addApiKey = function () {
		var modalInstance = $uibModal.open({
			templateUrl: 'views/users/apikey/apikey.model.html',
			controller: 'ModalAddApiKeyCtrl',
			windowClass: "animated fadeIn",
		});
		modalInstance.result.then(function (apiKey) {
			let headers = { "User-UUID": $scope.cur_user.uuid, "Token": $scope.cur_user.token };
			ApiKeyService.addApiKey(apiKey, headers, function (response) {
				if (angular.isDefined(response.status) && response.status === 201) {
					toaster.pop({
						type: "success",
						title: $translate.instant("TOASTER.SUCCESS_TITLE"),
						body: $translate.instant("TOASTER.SUCCESS_ADD_BODY", { template: $translate.instant("USER.API_KEY") }),
						showCloseButton: true,
					});
					$scope.getAllApiKeys();
				} else {
					toaster.pop({
						type: "error",
						title: $translate.instant("TOASTER.ERROR_ADD_BODY", { template: $translate.instant("USER.API_KEY") }),
						body: $translate.instant(response.data.description),
						showCloseButton: true,
					});
				}
			});
		}, function () {

		});
	};

	$scope.editApiKey = function (apiKey) {
		var modalInstance = $uibModal.open({
			windowClass: "animated fadeIn",
			templateUrl: 'views/users/apikey/apikey.model.html',
			controller: 'ModalEditApiKeyCtrl',
			resolve: {
				params: function () {
					return {
						apiKey: angular.copy(apiKey)
					};
				}
			}
		});
		modalInstance.result.then(function (modifiedApiKey) {
			let headers = { "User-UUID": $scope.cur_user.uuid, "Token": $scope.cur_user.token };
			ApiKeyService.editApiKey(modifiedApiKey, headers, function (response) {
				if (angular.isDefined(response.status) && response.status === 200) {
					toaster.pop({
						type: "success",
						title: $translate.instant("TOASTER.SUCCESS_TITLE"),
						body: $translate.instant("TOASTER.SUCCESS_UPDATE_BODY", { template: $translate.instant("USER.API_KEY") }),
						showCloseButton: true,
					});
					$scope.getAllApiKeys();
				} else {
					toaster.pop({
						type: "error",
						title: $translate.instant("TOASTER.ERROR_UPDATE_BODY", { template: $translate.instant("USER.API_KEY") }),
						body: $translate.instant(response.data.description),
						showCloseButton: true,
					});
				}
			});
		}, function () {
			//do nothing;
		});
	};

	$scope.deleteApiKey = function (apiKey) {
		SweetAlert.swal({
			title: $translate.instant("SWEET.TITLE"),
			text: $translate.instant("SWEET.TEXT"),
			type: "warning",
			showCancelButton: true,
			confirmButtonColor: "#DD6B55",
			confirmButtonText: $translate.instant("SWEET.CONFIRM_BUTTON_TEXT"),
			cancelButtonText: $translate.instant("SWEET.CANCEL_BUTTON_TEXT"),
			closeOnConfirm: true,
			closeOnCancel: true
		},
		function (isConfirm) {
			if (isConfirm) {
				let headers = { "User-UUID": $scope.cur_user.uuid, "Token": $scope.cur_user.token };
				ApiKeyService.deleteApiKey(apiKey, headers, function (response) {
					if (angular.isDefined(response.status) && response.status === 204) {
						toaster.pop({
							type: "success",
							title: $translate.instant("TOASTER.SUCCESS_TITLE"),
							body: $translate.instant("TOASTER.SUCCESS_DELETE_BODY", { template: $translate.instant("USER.API_KEY") }),
							showCloseButton: true,
						});
						$scope.getAllApiKeys();
					} else {
						toaster.pop({
							type: "error",
							title: $translate.instant("TOASTER.ERROR_DELETE_BODY", { template: $translate.instant("USER.API_KEY") }),
							body: $translate.instant(response.data.description),
							showCloseButton: true,
						});
					}
				});
			}
		});
	};

	$scope.getAllApiKeys();

});

app.controller('ModalAddApiKeyCtrl', function ($scope, $uibModalInstance) {
	$scope.operation = "USER.ADD_API_KEY";
	$scope.apiKey = {
		created_datetime_utc:moment(),
        expires_datetime_utc:moment().add(1,'years'),
	};
	$scope.flag = false;
	$scope.dtOptions = {
        locale:{
            format: 'YYYY-MM-DD HH:mm:ss',
            applyLabel: "OK",
            cancelLabel: "Cancel",
        },
        timePicker: true,
        timePicker24Hour: true,
        timePickerIncrement: 15,
        singleDatePicker: true,
    };
	$scope.ok = function () {
		$scope.apiKey.created_datetime_utc = $scope.apiKey.created_datetime_utc.format().slice(0,19);
        $scope.apiKey.expires_datetime_utc = $scope.apiKey.expires_datetime_utc.format().slice(0,19);
		$uibModalInstance.close($scope.apiKey);
	};

	$scope.cancel = function () {
		$uibModalInstance.dismiss('cancel');
	};
});

app.controller('ModalEditApiKeyCtrl', function ($scope, 
	$uibModalInstance, 
	params) {
	$scope.operation = "USER.EDIT_API_KEY";
	$scope.apiKey = params.apiKey;
	$scope.flag = false;
	$scope.dtOptions = {
        locale:{
            format: 'YYYY-MM-DD HH:mm:ss',
            applyLabel: "OK",
            cancelLabel: "Cancel",
        },
        timePicker: true,
        timePicker24Hour: true,
        timePickerIncrement: 15,
        singleDatePicker: true,
    };

	$scope.ok = function () {
		$scope.apiKey.created_datetime_utc = moment($scope.apiKey.created_datetime_utc).format().slice(0,19);
        $scope.apiKey.expires_datetime_utc = moment($scope.apiKey.expires_datetime_utc).format().slice(0,19);
		$uibModalInstance.close($scope.apiKey);
	};

	$scope.cancel = function () {
		$uibModalInstance.dismiss('cancel');
	};

});