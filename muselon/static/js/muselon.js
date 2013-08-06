var muselon = angular.module('muselon', ['ngResource', 'ngSanitize'])

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
	return $resource($SCRIPT_ROOT+ '/characters/user/:userId/world/:worldId', {userId: 1, worldId: 1}, 
	{update: {method: 'PUT', data:{name:'@name'}, isArray: false}}

);
})

.controller('ThreadCtrl', function($scope, socketio, commentFactory, characterFactory, $http){
	
	commentblocksObj = commentFactory.get({threadId: 1}, function() {
			$scope.commentblocks = commentblocksObj.json_list;
			console.log($scope.commentblocks);
	});
	
	charactersObj = characterFactory.get({userId: 1, worldId: 1}, function() {
		$scope.availableCharacters = charactersObj.json_list;
		console.log($scope.availableCharacters);
		$scope.post.selectedCharacterName = $scope.availableCharacters[0].name;
		$scope.post.selectedCharacterId = $scope.availableCharacters[0].id;

	});
		

	$scope.post = {type: "description", text: ""};

	$scope.$watch("post.selectedCharacterName", function() {
		for (var i=0; i<$scope.availableCharacters.length; i++){
			if ($scope.availableCharacters[i].name == $scope.post.selectedCharacterName) {
					$scope.post.selectedCharacterId = $scope.availableCharacters[i].id;
			}
		}
	});
		
	$scope.submitPost = function () {
		if (this.post.text) {
		
			charId = this.post.selectedCharacterId;
		
			if ($scope.post.type == "description") {
				console.log('emit description');
				socketio.emit('description_post', {"text": this.post.text, "charId": charId});
			} else if ($scope.post.type == "dialogue") {
				console.log('emit dialogue');
				socketio.emit('dialogue_post', {"text": this.post.text, "charId": charId});
			} else if ($scope.post.type == "challenge") {
				socketio.emit('challenge_post', this.post.text, this.stat);
			}
			this.post.text = '';
		}
	}
	
	$scope.append = function () {
		
	}
	
	socketio.on("updateComments", function () {
		commentblocksObj = commentFactory.get({threadId: 1}, function() {
			$scope.commentblocks = commentblocksObj.json_list;
			console.log($scope.commentblocks);
		})
	})
	
})

.controller('ProfileCtrl', function($scope, socketio, characterFactory, $http){
	charactersObj = characterFactory.get({userId: 1, worldId: 1}, function() {
		$scope.characters = charactersObj.json_list;
	});
	
	$scope.addCharacter = function () {
		if (this.characterName) {
			
			console.log("Adding character");
			console.log(this.characterName);

			charactersObj.$update({name: this.characterName});
			
			this.characterName = '';
		}
	}
	
})

;




