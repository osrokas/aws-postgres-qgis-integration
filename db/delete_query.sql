BEGIN;

	DELETE FROM panoramatobatchmap pb 
	WHERE pb.panoramauid in (
		SELECT pn.uid FROM panoramas pn
		WHERE pn.tripuid = 3
	);

	DELETE FROM panoramatobatchmap p
	WHERE p.batchuid in (
		SELECT e.uid FROM executionbatches e
		WHERE e.pipelineexecutionuid in (
		 	SELECT pp.tripuid FROM pipelineexecutions pp 
		 	WHERE pp.uid = 3
		 )
	);

	DELETE FROM executionbatches e 
	WHERE e.pipelineexecutionuid in (
		SELECT p.tripUid FROM pipelineexecutions p
		WHERE p.tripuid = 3
	);
	
	DELETE FROM pipelinelog
	WHERE tripuid = 3;

	DELETE FROM pipelineexecutions
	WHERE tripuid = 3;

	DELETE FROM tripsettings
	WHERE tripuid = 3;

	DELETE FROM panoramas
	WHERE tripuid = 3;

	DELETE FROM trips 
	WHERE uid = 3;
	
COMMIT;
