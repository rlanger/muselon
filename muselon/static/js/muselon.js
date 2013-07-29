var muselon = angular.module('muselon', ['ngResource'])

.config(function($interpolateProvider) {
	$interpolateProvider.startSymbol('[[');
	$interpolateProvider.endSymbol(']]');
})

.factory('socketio', function ($rootScope) {
	var WEB_SOCKET_SWF_LOCATION = '/static/js/socketio/WebSocketMain.swf', 
		socket = io.connect("/threadspace");
  return {
    on: function (eventName, callback) {
      socket.on(eventName, function () {  
        var args = arguments;
        $rootScope.$apply(function () {
          callback.apply(socket, args);
        });
      });
    },
    emit: function (eventName, data, callback) {
      socket.emit(eventName, data, function () {
        var args = arguments;
        $rootScope.$apply(function () {
          if (callback) {
            callback.apply(socket, args);
          }
        });
      })
    }
  };
})


.factory("commentFactory", function($resource){
	return $resource($SCRIPT_ROOT+ '/thread/:threadId', {threadId: 1});
})

.factory("characterFactory", function($resource){
	return $resource($SCRIPT_ROOT+ '/characters/user/:userId/world/:worldId', {userId: 1, worldId: 1});
})

.controller('ThreadCtrl', function($scope, socketio, commentFactory, characterFactory, $http){
	
	commentblocksObj = commentFactory.get({threadId: 1}, function() {
			$scope.commentblocks = commentblocksObj.json_list;
			console.log($scope.commentblocks);
	});
	
	charactersObj = characterFactory.get({userId: 1, worldId: 1}, function() {
		$scope.availableCharacters = charactersObj.json_list;
		console.log($scope.availableCharacters);
		$scope.character = $scope.availableCharacters[0].name;

	});
		
	$scope.postType = "description";
	
	$scope.submitPost = function () {
		if (this.post) {
			if ($scope.postType = "description") {
				socketio.emit('post', this.post, 1);
			} else if ($scope.postType = "dialogue") {
				socketio.emit('dialogue_post', this.post, this.icon);
			} else if ($scope.postType = "challenge") {
				socketio.emit('challenge_post', this.post, this.stat);
			}
			this.post = '';
		}
	}
	
	$scope.append = function () {
		
	}
	
	socketio.on("updateComments", function () {
		commentsObj = commentFactory.get({threadId: 1}, function() {
			$scope.comments = commentsObj.json_list;
			console.log($scope.comments);
		})
	})
	
})


;