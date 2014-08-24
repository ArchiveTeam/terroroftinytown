(function(){

"use strict";

var WSController = function(endpoint){
	this.ws = new WebSocket("ws://" + window.location.host + window.location.pathname + endpoint);
	this.ws.onmessage = this._onmessage.bind(this);
	this.stats = {
		'live': [],
		'lifetime': {},
		'global': [0, 0],
	};
};

WSController.prototype._onmessage = function(evt){
	var message = JSON.parse(evt.data);

	if(message.live){
		this.stats.live = message.live;
	}

	if(message.lifetime){
		this.stats.lifetime = message.lifetime;
	}

	if(message.global){
		this.stats.global = message.global;
	}

	if(message.live_new){
		this.stats.live.unshift(message.live_new);

		var lifetime = this.stats.lifetime[message.live_new.username];
		if(lifetime === undefined){
			lifetime = [0, 0];
			this.stats.lifetime[message.live_new.username] = lifetime;
		}
		lifetime[0] += message.live_new.found;
		lifetime[1] += message.live_new.scanned;

		this.stats.global[0] += message.live_new.found;
		this.stats.global[1] += message.live_new.scanned;		
	}

	this.onMessage(message);
};

WSController.prototype.onMessage = function(message){
};

var app = angular.module("stats", []);

app.constant("endpoint", "api/live_stats");
app.constant("max_display", 30);

app.service("ws", ["endpoint", function(endpoint){
	return new WSController(endpoint);
}]);

app.filter("toArray", function(){
	return function(obj) {
		var result = [];
		angular.forEach(obj, function(val, key) {
			result.push([key, val]);
		});
		return result;
	};
});

app.controller("StatsController", ["$scope", "$filter", "ws", "max_display", function($scope, $filter, ws, max_display){
	$scope.stats = ws.stats;
	$scope.getScanned = function(item){
		return item[1][1];
	};
	ws.onMessage = function(){
		ws.stats.live.splice(29, ws.stats.live.length);
		// somehow computing this in page cause infinite digest cycles
		$scope.lifetime = $filter("toArray")(ws.stats.lifetime);
		
		$scope.$apply();
	};
}]);

})();