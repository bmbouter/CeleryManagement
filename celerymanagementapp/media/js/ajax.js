var CMA = (typeof CMA === "undefined" || !CMA) ? {} : CMA;
CMA.Core = (typeof CMA.Core === "undefined" || !CMA.Core) ? {} : CMA.Core;

CMA.Core.ajax = (function() {
    var urls = {},

        loadUrls = function() {
            root_url = "/celerymanagementapp/";
            
            urls = {
                get_tasks_url: root_url + "task/all/list/",
                get_workers_url: root_url + "worker/all/list/",
                tasks_per_worker_url: root_url + "task/all/dispatched/byworker/count/",
                task_url: root_url + "view/dispatched_tasks/",
                pending_tasks_url: root_url + "task/all/dispatched/pending/count/",
                worker_processes_url: root_url + "worker/all/subprocess/count/",
                shutdown_worker_url: root_url + "worker/<placeHolder>/shutdown/",
                query_dispatched_tasks_url: root_url + "xy_query/dispatched_tasks/",
                task_url: "/celerymanagementapp/view/task/",
                worker_url: "/celerymanagementapp/view/task/",
                create_out_of_band_worker_url: root_url + "outofbandworker/",
                create_provider_url: root_url + "provider/",
                get_images_url: root_url + "provider/images/",
            };
        },
        loadTestUrls = function() {
            var root_url = "/celerymanagementapp/site_media/test_data/";
            var post_root_url = "/celerymanagementapp/test/post/";
            
            urls = {
                get_tasks_url: root_url + "tasks.json",
                get_workers_url: root_url + "workers.json",
                tasks_per_worker_url: root_url + "tasks_per_worker.json",
                pending_tasks_url: root_url + "tasks_pending.json",
                worker_processes_url: root_url + "worker_processes.json",
                shutdown_worker_url: post_root_url + "worker/<placeHolder>/shutdown/",
                query_dispatched_tasks_url: post_root_url + "xy_query/dispatched_tasks/",
                task_url: "/celerymanagementapp/test/view/task/",
                worker_url: "/celerymanagementapp/test/view/worker/",
                chart_data_url: root_url + "chart/enumerate-1.json",
                create_out_of_band_worker_url: post_root_url + "outofbandworker/",
                create_provider_url: post_root_url + "provider/",
                get_images_url: post_root_url + "provider/images/",
            };
        },
        getTasks = function(callbackFunction){
            $.getJSON(urls.get_tasks_url, callbackFunction);
        },
        getWorkers = function(callbackFunction){
            $.getJSON(urls.get_workers_url, callbackFunction);
        },
        getTasksPerWorker = function(callbackFunction){
            $.getJSON(urls.tasks_per_worker_url, callbackFunction);
        },
        getPendingTasks = function(callbackFunction){
            $.getJSON(urls.pending_tasks_url, callbackFunction);
        },
        getWorkerProcesses = function(callbackFunction){
            $.getJSON(urls.worker_processes_url, callbackFunction);
        },
        postShutdownWorker = function(workerName, callbackFunction){
            $.post(urls.shutdown_worker_url.replace("<placeHolder>", workerName), callbackFunction);
        },
        getDispatchedTasksData = function(query, callbackFunction) {
            $.post(urls.query_dispatched_tasks_url, query, callbackFunction);
        },
        postCreateOutOfBandWorkerNode = function(callbackFunction){
            $.post(urls.create_out_of_band_worker_url, $('#blankOutOfBandForm').serialize(), callbackFunction);
        },
        postCreateProvider = function(callbackFunction){
            $.post(urls.create_provider_url, $('#blankProviderForm').serialize(), callbackFunction);
        },
        postGetImages = function(callbackFunction){
            $.post(urls.get_images_url, $('#blankProviderForm').serialize(), callbackFunction, "json");
        };

    return {
        urls: urls,
        loadUrls: loadUrls,
        loadTestUrls: loadTestUrls,
        getTasks: getTasks,
        getWorkers: getWorkers,
        getTasksPerWorker: getTasksPerWorker,
        getPendingTasks: getPendingTasks,
        getWorkerProcesses: getWorkerProcesses,
        postShutdownWorker: postShutdownWorker,
        getDispatchedTasksData: getDispatchedTasksData,
        postCreateOutOfBandWorkerNode: postCreateOutOfBandWorkerNode,
        postCreateProvider: postCreateProvider,
        postGetImages: postGetImages,
    };
}());
