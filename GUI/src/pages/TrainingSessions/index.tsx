import { FC } from 'react';
import { useTranslation } from 'react-i18next';
import TrainingSessionCard from 'components/molecules/TrainingSessionCard';
import { useTrainingSessions } from 'hooks/useTrainingSessions';

const TrainingSessions: FC = () => {
  const { t } = useTranslation();
  const progresses = useTrainingSessions();

  return (
    <div>
      <div className="container">
        <div className="title_container">
          <div className="title">{t('trainingSessions.title')}</div>
        </div>
        {progresses?.map((session) => (
          <TrainingSessionCard
            key={session.id}
            modelName={session.modelName}
            version={`V${session?.majorVersion}.${session?.minorVersion}`}
            isLatest={session.latest}
            status={session.trainingStatus}
            progress={session.progressPercentage}
            trainingMessage={session.trainingMessage}
          />
        ))}
      </div>
    </div>
  );
};

export default TrainingSessions;
